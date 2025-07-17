import json
import time
import argparse
import llm
import os

from pydantic import BaseModel, Field, ValidationError, field_validator
from dotenv import load_dotenv

from utils import delete_game_cache
from bot import Bot, Actions, State

from typing import Any, List, Literal, Optional, Tuple, TypeVar, Union

from typing import TypedDict

from jokers import jokers_dict, scoring_rules, shop_strategy, blinds_dict

# Load environment variables from .env file
load_dotenv()


# Configure API key for Gemini
def configure_gemini_api_key():
    """Configure the Google AI API key for Gemini."""
    api_key = os.getenv("LLM_GEMINI_KEY")

    if not api_key:
        print("Warning: LLM_GEMINI_KEY environment variable not set.")
        print("To use Gemini, please:")
        print("1. Get your API key from: https://aistudio.google.com/app/apikey")
        print("2. Add your API key to the .env file: LLM_GEMINI_KEY=your_api_key_here")
        print("3. Or set it as an environment variable:")
        print("   export LLM_GEMINI_KEY='your_api_key_here'")
        return False

    # The llm library will automatically use the LLM_GEMINI_KEY environment variable
    # No need to explicitly set it via the library
    return True


# Configure LLM for Gemini
api_key_configured = configure_gemini_api_key()

try:
    llm_model = llm.get_model("gemini/gemini-2.5-flash")
    if api_key_configured:
        print("Gemini 2.5 Flash model configured successfully with API key")
    else:
        print("Gemini 2.5 Flash model configured but no API key set")
except Exception as e:
    print(f"Warning: Could not configure Gemini model: {e}")
    print("Make sure you have the Gemini plugin installed: uv add llm-gemini")
    llm_model = None


class Card(TypedDict):
    suit: str
    label: str
    value: int
    name: str
    debuff: str
    card_key: str
    cost: int
    ability: Any


class Tag(TypedDict):
    name: str


class Blinds(TypedDict):
    ondeck: str
    boss: str
    name: str
    skip_tag: dict[str, str]


class Ante(TypedDict):
    blinds: Blinds


class Round(TypedDict):
    dollars_to_be_earned: int
    hands_left: int
    discards_left: int


class Joker(TypedDict):
    label: str
    cost: int
    debuff: bool


class Voucher(TypedDict):
    label: str
    cost: int
    debuff: bool


class Shop(TypedDict):
    reroll_cost: int
    boosters: List[Card]
    cards: List[Joker]
    vouchers: List[Voucher]


class GameState(TypedDict):
    state: State
    waitingFor: str
    waitingForAction: bool
    bankrupt_at: int
    dollars: int
    chips: int
    current_round: Round
    round: int
    num_hands_played: int
    inflation: int
    state: int
    discount_percent: int
    interest_cap: int
    hand: List[Card]
    deck: List[Card]
    tags: List[Any]
    jokers: List[Joker]
    consumables: List[Card]
    shop: Union[Shop, None]
    pack_cards: List[Card]


def game_state_to_prompt(gamestate: GameState) -> str:
    """Convert the game state to a string representation for LLM prompts."""
    output_str = ""
    if gamestate.get("waitingFor", None) == "select_shop_action":
        output_str += shop_state_to_prompt(gamestate)
    elif gamestate.get("waitingFor", None) == "select_booster_action":
        output_str += booster_pack_to_prompt(gamestate)
    elif gamestate.get("waitingFor", None) == "select_cards_from_hand":
        output_str += select_cards_to_prompt(gamestate)
    elif gamestate.get("waitingFor", None) == "skip_or_select_blind":
        output_str += blind_to_prompt(gamestate)
    elif gamestate.get("waitingFor", None) == "use_or_sell_consumables":
        output_str += consumables_to_prompt(gamestate)

    return output_str


def shop_state_to_prompt(gamestate: GameState) -> str:
    """Convert the shop state to a string representation for LLM prompts."""
    shop = gamestate.get("shop", {})
    if not shop:
        return "No shop data available."

    shop_str = "You are in the Shop.\n"
    shop_str += f"Current Dollars: {gamestate.get('dollars', 0)}\n"
    shop_str += f"Current Discount Percent: {gamestate.get('discount_percent', 0)}%\n"
    shop_str += f"Reroll Cost: {shop.get('reroll_cost', 0)}\n"
    shop_str += "You can buy Boosters:\n"
    for i, booster in enumerate(shop.get("boosters", [])):
        shop_str += f"- {booster['label']} (Cost: {booster['cost']}, index: {i})\n"
    if not gamestate.get("boosters"):
        shop_str += "No boosters available.\n"
    shop_str += "You can buy Jokers:\n"
    for i, joker in enumerate(shop.get("cards", [])):
        shop_str += f"- {joker['label']} (Description: {jokers_dict[joker['label']]}, Cost: {joker['cost']}, index: {i})\n"
    if not gamestate.get("cards"):
        shop_str += "No jokers available.\n"
    shop_str += "You can buy Vouchers:\n"
    for i, voucher in enumerate(shop.get("vouchers", [])):
        shop_str += f"- {voucher['label']} (Cost: {voucher['cost']}, index: {i})\n"
    if not gamestate.get("vouchers"):
        shop_str += "No vouchers available.\n"

    jokers = gamestate.get("jokers", [])
    shop_str += f"You have {len(jokers)} out of the default 5 maximum.\n You have the following jokers:\n"
    for i, joker in enumerate(jokers):
        shop_str += f"- {joker['label']} (Description: {jokers_dict[joker['label']]})\n"
    if not gamestate.get("jokers"):
        shop_str += "You have no jokers.\n"

    shop_str += f"You have {len(gamestate.get('consumables', []))} out of the default 2 maximum.\n"
    shop_str += "You already have the following consumables:\n"
    for i, consumable in enumerate(gamestate.get("consumables", [])):
        shop_str += f"- {consumable['label']}\n"
    if not gamestate.get("consumables"):
        shop_str += "You have no consumables.\n"

    shop_str += current_deck_to_prompt(gamestate)

    shop_str += shop_strategy

    return shop_str


def current_deck_to_prompt(gamestate: GameState) -> str:
    """Convert the current deck to a string representation for LLM prompts."""
    deck = gamestate.get("deck", [])
    if not deck:
        return "No cards in the current deck."

    deck_str = "Your current deck:\n"
    for card in deck:
        deck_str += f"- {card['name']}\n"

    return deck_str


def booster_pack_to_prompt(gamestate: GameState) -> str:
    """Convert the booster pack to a string representation for LLM prompts."""
    booster_str = "Booster Pack:\n"
    for i, card in enumerate(gamestate.get("pack_cards", [])):
        booster_str += f"- {card.get('name', '')} {card.get('label', '')} (index: {i}, Ability: `{json.dumps(card['ability'])}`)\n"
    if not gamestate.get("pack_cards"):
        booster_str += "No cards available in the booster pack.\n"

    if gamestate.get("hand"):
        booster_str += "Your Hand:\n"
        for i, card in enumerate(gamestate.get("hand", [])):
            booster_str += f"- {card['name']} (index: {i})\n"

    return booster_str


def select_cards_to_prompt(gamestate: GameState) -> str:
    """Convert the current hand to a string representation for LLM prompts."""
    return_str = "You are selecting cards from your hand.\n"

    current_round = gamestate.get("current_round", {})
    return_str += f"Your score is: {gamestate.get('chips', 0)}\n"
    return_str += f"Score at least: {current_round.get('dollars_to_be_earned', 0)}\n"
    return_str += f"Hands left: {current_round.get('hands_left', 0)}\n"
    return_str += f"Discards left: {current_round.get('discards_left', 0)}\n"
    return_str += f"If you don't score at least {current_round.get('dollars_to_be_earned', 0)} before you run out of hands, you will lose the game.\n"

    blinds = gamestate.get("ante", {}).get("blinds", {})
    if blinds:
        return_str += f"Current Blind: {blinds.get('name', 'Unknown')}\n"

        blind_info = blinds_dict.get(blinds.get("name", ""), None)
        if blind_info:
            return_str += f"Blind Description: {blind_info.get('description', 'No description available')}\n"
            return_str += f"A reward of {blind_info.get('reward', 0)} will be given for meeting {blind_info.get('score_requirement', '')} {current_round.get('dollars_to_be_earned', 0)}.\n"

    jokers = gamestate.get("jokers", [])
    return_str += "Your Jokers are:\n"
    for i, card in enumerate(jokers):
        return_str += f"- {card['label']} (Description: {jokers_dict[card['label']]})\n"
    if not gamestate.get("jokers"):
        return_str += "You have no jokers.\n"

    hand = gamestate.get("hand", [])
    return_str += "Your Hand is:\n"
    for i, card in enumerate(hand):
        return_str += f"- {card['name']} {card['label']} (index: {i})\n"

    return_str += current_deck_to_prompt(gamestate)

    return_str += scoring_rules

    return return_str


def blind_to_prompt(gamestate: GameState) -> str:
    """Convert the blind state to a string representation for LLM prompts."""
    blinds = gamestate.get("ante", {}).get("blinds", {})
    if not blinds:
        return "No blind data available."

    blind_str = f"You are deciding whether to skip or select the {blinds.get('ondeck', 'None')} blind.\n"
    blind_info = blinds_dict.get(blinds.get("ondeck", ""), None)
    if blind_info:
        blind_str += f"Blind Description: {blind_info.get('description', 'No description available')}\n"
        blind_str += f"A reward of {blind_info.get('reward', 0)} will be given for meeting {blind_info.get('score_requirement', '')}.\n"

    boss_blind_info = blinds_dict.get(blinds.get("boss", ""), None)
    blind_str += f"Upcoming Boss Blind: {blinds.get('boss', 'None')} - {boss_blind_info.get('description', 'No description available')}\n"
    blind_str += f"A reward of {boss_blind_info.get('reward', 0)} will be given for beating the boss by {boss_blind_info.get('score_requirement', '')}.\n"

    blind_str += f"If you skip this blind you will get this tag `{json.dumps(blinds.get('skip_tag', {}))}` but it won't apply until you get to the shop.\n"
    blind_str += f"If you skip the Small blind you will immediately progress to the Big Blind without visiting the shop.\n"
    blind_str += f"If you skip the Big blind you will immediately progress to the Boss Blind without visiting the shop.\n"
    blind_str += f"If you select the blind you will be able to earn money and then visit the shop.\n"

    blind_str += f"Current Chips: {gamestate.get('chips', 0)}\n"
    blind_str += f"Round: {gamestate.get('round', 0)}\n"
    blind_str += f"Current Dollars: {gamestate.get('dollars', 0)}\n"
    blind_str += f"Inflation: {gamestate.get('inflation', 0)}%\n"

    jokers = gamestate.get("jokers", [])
    blind_str += f"You have {len(jokers)} out of the default 5 maximum.\n You have the following jokers:\n"
    for i, joker in enumerate(jokers):
        blind_str += (
            f"- {joker['label']} (Description: {jokers_dict[joker['label']]})\n"
        )
    if not gamestate.get("jokers"):
        blind_str += "You have no jokers.\n"

    blind_str += f"You have {len(gamestate.get('consumables', []))} out of the default 2 maximum.\n"
    blind_str += "You already have the following consumables:\n"
    for i, consumable in enumerate(gamestate.get("consumables", [])):
        blind_str += f"- {consumable['label']}\n"
    if not gamestate.get("consumables"):
        blind_str += "You have no consumables.\n"

    blind_str += current_deck_to_prompt(gamestate)

    return blind_str


def consumables_to_prompt(gamestate: GameState) -> str:
    """Convert the consumables state to a string representation for LLM prompts."""
    consumables = gamestate.get("consumables", [])

    consumables_str = "Your consumables:\n"
    for i, consumable in enumerate(consumables):
        consumables_str += f"- {consumable['label']} (index: {i})\n"
    if not consumables:
        consumables_str += "You have no consumables.\n"

    consumables_str += current_deck_to_prompt(gamestate)

    return consumables_str


# Skip or Select Blind Actions
# This action is used to either skip the blind or select it to play against it
SkipOrSelectBlindAction = Tuple[Actions.SELECT_BLIND] | Tuple[Actions.SKIP_BLIND]


class SkipOrSelectBlindModel(BaseModel):
    """Action to either skip or select a blind in the game."""

    action: Union[Literal["SELECT_BLIND"], Literal["SKIP_BLIND"]] = Field(
        description="Choose to either select the blind to play against it, or skip it to avoid the challenge"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


# Select Card Actions
# Play Cards, along with a list of indices to select from hand
PlayHandAction = Tuple[Actions.PLAY_HAND, List[int]]
# Discard Cards, along with a list of indices to discard from hand
DiscardHandAction = Tuple[Actions.DISCARD_HAND, List[int]]
RearrangeHandAction = Tuple[Actions.REARRANGE_HAND, List[int]]
RearrangeJokersAction = Tuple[Actions.REARRANGE_JOKERS, List[int]]

SelectCardsFromHandAction = (
    PlayHandAction | DiscardHandAction | RearrangeHandAction | RearrangeJokersAction
)


class SelectCardsFromHandModel(BaseModel):
    """Action to either play or discard cards from hand."""

    action: Union[
        Literal["PLAY_HAND"],
        Literal["DISCARD_HAND"],
        Literal["REARRANGE_JOKERS"],
        Literal["REARRANGE_HAND"],
    ] = Field(description="Choose an action.")
    indices: List[int] = Field(
        min_length=1,
        description="Array of indices of cards",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


# Shop Actions
BuyVoucherAction = Tuple[Actions.BUY_VOUCHER, List[int]]
BuyCardAction = Tuple[Actions.BUY_CARD, List[int]]
BuyBoosterAction = Tuple[Actions.BUY_BOOSTER, List[int]]
SellJokerAction = Tuple[Actions.SELL_JOKER, List[int]]
RerollShopAction = Tuple[Actions.REROLL_SHOP]
EndShopAction = Tuple[Actions.END_SHOP]
ShopAction = (
    BuyVoucherAction
    | BuyCardAction
    | BuyBoosterAction
    | SellJokerAction
    | RerollShopAction
    | EndShopAction
)


class ShopActionModel(BaseModel):
    """Action to perform in the shop."""

    action: Union[
        Literal["BUY_VOUCHER"],
        Literal["BUY_CARD"],
        Literal["BUY_BOOSTER"],
        Literal["REROLL_SHOP"],
        Literal["SELL_JOKER"],
        Literal["END_SHOP"],
    ] = Field(
        description="Choose to either buy a voucher, buy a joker, buy a booster, reroll the shop, sell jokers, or end the shop phase"
    )
    index: Optional[int] = Field(
        default=None,
        description="Index of the single item. If not applicable, this can be omitted.",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


# Booster Actions
# TODO: Not sure what the second list here is
SelectBoosterAction = Tuple[Actions.SELECT_BOOSTER_CARD, List[int], List[int]]
EndBoosterAction = Tuple[Actions.SKIP_BOOSTER_PACK]
BoosterAction = SelectBoosterAction | EndBoosterAction


class BoosterActionModel(BaseModel):
    """Action to perform in the booster phase."""

    action: Union[Literal["SELECT_BOOSTER_CARD"], Literal["SKIP_BOOSTER_PACK"]] = Field(
        description="Choose to either select a card from the booster pack or skip it."
    )
    indices: List[int] = Field(
        description="For most packs you can specify a single index. For a mega pack you can select two.",
    )
    card_indices: Optional[List[int]] = Field(
        default=None,
        description="If performing an action using certain tarot cards, this is the list of card indices to apply those tarot changes to",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


# Use or Sell Consumables Actions
UseConsumableAction = Tuple[Actions.USE_CONSUMABLE, List[int], List[int]]
SellConsumableAction = Tuple[Actions.SELL_CONSUMABLE, List[int]]
UseOrSellConsumablesAction = UseConsumableAction | SellConsumableAction


class UseOrSellConsumablesModel(BaseModel):
    """Action to either use or sell consumables in hand."""

    action: Union[Literal["USE_CONSUMABLE"], Literal["SELL_CONSUMABLE"]] = Field(
        description="Choose to either use consumables from hand, or sell them"
    )
    indices: List[int] = Field(
        description="List of indices of consumables to use or sell from hand, return an empty list to skip using or selling consumables",
    )
    card_indices: Optional[List[int]] = Field(
        default=None,
        description="If using certain tarot cards, this is the list of card indices to apply those tarot changes to",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


# Rearrange Consumables Actions
RearrangeConsumablesAction = Tuple[Actions.REARRANGE_CONSUMABLES, List[int]]


class RearrangeConsumablesModel(BaseModel):
    """Action to rearrange consumables in hand."""

    action: Literal["REARRANGE_CONSUMABLES"] = Field(
        description="Choose to rearrange consumables in hand. Return an empty list to skip rearranging consumables."
    )
    indices: List[int] = Field(
        description="List of indices of consumables to rearrange in hand",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the decision",
    )


T = TypeVar("T", bound=BaseModel)

SYSTEM_PROMPT = """
You are a mega genius Balatro player who can think strategically and creatively.
You are excellent at analyzing game states and making decisions based on the current situation.
You are a master of the Balatro game and understand all the rules, strategies, and nuances.
You can calculate the exact score of any hand you want to play based on the rules of Balatro.

Your task is to play Balatro, analyze the game state and make decisions based on the current situation.
Describe your reasoning for each decision you make. You can leave notes for yourself in the reasoning field.

You will receive the current game state and must respond in JSON format that matches the provided schema.

Before you respond, think through your reasoning step by step, and then take your action.
Respond with your thinking first, then the action you want to take as a valid JSON object based on the schema provided.
"""


class LLMBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_reasoning: Optional[str] = None

        # self.conversation = model.conversation(tools=[])
        # self.conversation.prompt(system=SYSTEM_PROMPT)

    def is_llm_ready(self) -> bool:
        """Check if the LLM is properly configured and ready to use."""
        return self.llm_model is not None and api_key_configured

    def _extract_json_from_response(self, text: str) -> str:
        """Extract JSON from a response that might contain extra text."""
        # Remove any markdown code blocks
        text = text.strip()

        # Remove markdown json code blocks if present
        if text.startswith("```json"):
            text = text[7:]  # Remove ```json
        if text.startswith("```"):
            text = text[3:]  # Remove ```
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```

        text = text.strip()

        # Try to find a complete JSON object
        brace_count = 0
        start_idx = -1

        for i, char in enumerate(text):
            if char == "{":
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    # Found a complete JSON object
                    return text[start_idx : i + 1]

        # Fallback: find the first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace : last_brace + 1]

        # If we can't find braces, return the original text
        return text

    def _query_llm(
        self,
        prompt: str,
        Schema: T,
    ) -> T:
        """Helper method to query the LLM with game state context."""

        print("--------------------- New Query -------------------")
        print(f"Game state:\n{self.G}")

        try:
            response = llm_model.prompt(
                f"""
{prompt}

{game_state_to_prompt(self.G)}

In the last turn that you played, you made the following reasoning:
{self.last_reasoning or "No previous reasoning."}

Schema:
```json
{Schema.model_json_schema()}
```
""",
                system=SYSTEM_PROMPT,
                google_search=False,  # Haven't seen noticeable improvements with this
                # gemini llm plugin doesn't support my schemas
                # schema=Schema,
            )
            print("--------------------- LLM Response -------------------")
            print(f"LLM prompt:\n{response.prompt}")
            raw_text = response.text()
            print(f"LLM raw response:\n{raw_text}")

            # Extract JSON from the response if there's extra text
            text = self._extract_json_from_response(raw_text)

            if text != raw_text:
                print(f"Extracted JSON:\n{text}")

            model = Schema.model_validate_json(
                text
            )  # Validate the response against the schema

            if model.reasoning:
                self.last_reasoning = f"{model.action} - {model.reasoning}"

            return model
        except ValidationError as ve:
            print("--")
            print("Validation error:", ve)
            # self.conversation.chain(
            #     f"{ve}\nPlease ensure your response matches the expected schema.",
            #     system="Do not respond to this message, the previous message will be sent again for you to respond to.",
            # )
            return self._query_llm(prompt, Schema)  # Retry with the same prompt
        except Exception as e:
            print("--")
            print("Error querying LLM:", e)
            return self._query_llm(prompt, Schema)  # Retry with the same prompt

    def skip_or_select_blind(self) -> SkipOrSelectBlindAction:
        """Decide whether to skip or select a blind based on the game state."""
        model: SkipOrSelectBlindModel = self._query_llm(
            prompt="Decide whether to skip or select a blind. You can only skip the small or big blind, not the boss blind.",
            Schema=SkipOrSelectBlindModel,
        )
        return (Actions[model.action],)

    def select_cards_from_hand(self) -> SelectCardsFromHandAction:
        model: SelectCardsFromHandModel = self._query_llm(
            prompt=f"""
Decide whether to:
- Play a hand,
- Discard cards from your hand,
- Rearrange cards in your hand, or
- Rearrange your jokers.

Don't try to win the round in a single hand, you have multiple hands and multiple discards.

When you play a hand, you must select the indices of the cards you want to play.
When you discard a hand, you must select the indices of the cards you want to discard. By default you can discard a maximum of 5 cards at a time.

If you're running low on discards, but have plenty of hands, strategically play a hand to save the discards for later. You can use playing a hand as a way to discard into better hands later on.
If you're playing a hand, carefully think through the Balatro scoring rules.

If you run out of hands without meeting the target score, you will lose the game.

You can strategically rearrange your jokers, or your hand to increase your score.
The score is calculated from left to right, so prefer adding on the left, and multiplying on the right.
""",
            Schema=SelectCardsFromHandModel,
        )
        return (Actions[model.action], make_one_based(model.indices))

    def select_shop_action(self) -> ShopAction:
        model: ShopActionModel = self._query_llm(
            prompt=f"Decide whether to buy jokers, boosters or vouchers in the shop. You can also sell jokers, or rearrange the order of jokers.\n",
            Schema=ShopActionModel,
        )
        action = Actions[model.action]
        if action in (Actions.END_SHOP, Actions.REROLL_SHOP):
            # If the action is to end or reroll the shop, no index is needed
            return (action,)
        if model.index is None:
            print("Warning: No index provided for shop action, trying again.")
            return self.select_shop_action()  # Retry if no index is provided
        return (action, make_one_based([model.index]))

    def select_booster_action(self) -> BoosterAction:
        """Decide whether to select a card from the booster pack or skip it."""
        model: BoosterActionModel = self._query_llm(
            prompt="""Decide whether to select a card from the booster pack or skip selecting a card.
Only skip the booster pack if you have no cards you want to select.
These cards are already paid for, ignore any cost associated with them.
When selecting a tarot or spectrum card from the booster pack make sure to apply it to the correct indices in hand (`card_indices`)
""",
            Schema=BoosterActionModel,
        )
        action = Actions[model.action]
        if action == Actions.SKIP_BOOSTER_PACK:
            # If the action is to skip the booster pack, no indices are needed
            return (Actions.SKIP_BOOSTER_PACK,)

        if model.card_indices:
            return (
                action,
                make_one_based(model.indices),
                make_one_based(model.card_indices),
            )

        return (action, make_one_based(model.indices))

    def use_or_sell_consumables(self) -> UseOrSellConsumablesAction:
        if not self.G.get("consumables"):
            # If there are no consumables, skip this action
            return (Actions.USE_CONSUMABLE, [])

        model: UseOrSellConsumablesModel = self._query_llm(
            prompt="Decide whether to use or sell consumables.",
            Schema=UseOrSellConsumablesModel,
        )
        action = Actions[model.action]
        if action == Actions.SELL_CONSUMABLE:
            return (action, make_one_based(model.indices))
        if not model.card_indices:
            # If no card indices are provided, assume no tarot cards are used
            return (action, make_one_based(model.indices))
        return (
            action,
            make_one_based(model.indices),
            make_one_based(model.card_indices),
        )


def make_one_based(indices: List[int]) -> List[int]:
    """Convert zero-based indices to one-based indices."""
    return [index + 1 for index in indices]


if __name__ == "__main__":
    # do we want to delete all our gamestate_cache files and start with a fresh state?
    parser = argparse.ArgumentParser(description="Game cache management script")
    parser.add_argument(
        "--delete-game-cache",
        action="store_true",
        help="Delete all .json files in the gamestate_cache directory",
    )
    args = parser.parse_args()

    if args.delete_game_cache:
        delete_game_cache()

    # creating balatro bot
    mybot = LLMBot(deck="Blue Deck", stake=1, seed=None, challenge=None, bot_port=12347)

    time.sleep(1)

    print("Starting bot...")
    mybot.run()
