import json
import time
import argparse
import llm
import os
import re

from pydantic import BaseModel, Field, ValidationError, field_validator
from dotenv import load_dotenv

from utils import delete_game_cache
from bot import Bot, Actions, State

from typing import Any, List, Literal, Optional, Tuple, TypeVar, Union

from typing import TypedDict

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


class GameState(TypedDict):
    state: State
    hand: List[Card]
    jokers: List[Any]
    consumables: List[Any]


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
        description="Optional reasoning for the decision",
    )


# Select Card Actions
# Play Cards, along with a list of indices to select from hand
PlayHandAction = Tuple[Actions.PLAY_HAND, List[int]]
# Discard Cards, along with a list of indices to discard from hand
DiscardHandAction = Tuple[Actions.DISCARD_HAND, List[int]]
SelectCardsFromHandAction = PlayHandAction | DiscardHandAction


class SelectCardsFromHandModel(BaseModel):
    """Action to either play or discard cards from hand."""

    action: Union[Literal["PLAY_HAND"], Literal["DISCARD_HAND"]] = Field(
        description="Choose to either play cards from hand, or discard them"
    )
    indices: List[int] = Field(
        min_length=1,
        description="List of indices of cards to play or discard from hand",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# Shop Actions
BuyVoucherAction = Tuple[Actions.BUY_VOUCHER, List[int]]
BuyCardAction = Tuple[Actions.BUY_CARD, List[int]]
BuyBoosterAction = Tuple[Actions.BUY_BOOSTER, List[int]]
RerollShopAction = Tuple[Actions.REROLL_SHOP]
EndShopAction = Tuple[Actions.END_SHOP]
ShopAction = (
    BuyVoucherAction
    | BuyCardAction
    | BuyBoosterAction
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
        Literal["END_SHOP"],
    ] = Field(
        description="Choose to either buy a voucher, buy a joker, buy a booster, reroll the shop, or end the shop phase"
    )
    indices: Optional[List[int]] = Field(
        default=None,
        max_length=1,
        description="List of indices of cards, boosters, or vouchers to purchase (maximum of one)",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# Booster Actions
# TODO: Not sure what the second list here is
SelectBoosterAction = Tuple[Actions.SELECT_BOOSTER_CARD, List[int], List[int]]
EndBoosterAction = Tuple[Actions.SKIP_BOOSTER_PACK]
BoosterAction = SelectBoosterAction | EndBoosterAction


class BoosterActionModel(BaseModel):
    """Action to perform in the booster phase."""

    action: Union[Literal["SELECT_BOOSTER_CARD"], Literal["SKIP_BOOSTER_PACK"]] = Field(
        description="Choose to either select a card from the booster pack or skip it"
    )
    indices: List[int] = Field(
        description="List of indices of cards to select from the booster pack",
    )
    card_indices: Optional[List[int]] = Field(
        default=None,
        description="If performing an action using certain tarot cards, this is the list of card indices to apply those tarot changes to",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# Sell Joker Actions
SellJokerAction = Tuple[Actions.SELL_JOKER, List[int]]


class SellJokerModel(BaseModel):
    """Action to sell jokers from hand."""

    action: Literal["SELL_JOKER"] = Field(description="Choose to sell jokers from hand")
    indices: List[int] = Field(
        description="List of indices of jokers to sell from hand, return an empty list to skip selling jokers",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# Rearrange Jokers Actions
RearrangeJokersAction = Tuple[Actions.REARRANGE_JOKERS, List[int]]


class RearrangeJokersModel(BaseModel):
    """Action to rearrange jokers in hand."""

    action: Literal["REARRANGE_JOKERS"] = Field(
        description="Choose to rearrange jokers in hand"
    )
    indices: List[int] = Field(
        description="List of indices of jokers to rearrange in hand",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# Use or Sell Consumables Actions
UseConsumableAction = Tuple[Actions.USE_CONSUMABLE, List[int]]
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
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
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
        description="Optional reasoning for the decision",
    )


# Rearrange Hand Actions
RearrangeHandAction = Tuple[Actions.REARRANGE_HAND, List[int]]


class RearrangeHandModel(BaseModel):
    """Action to rearrange cards in hand."""

    action: Literal["REARRANGE_HAND"] = Field(
        description="Choose to rearrange cards in hand"
    )
    indices: List[int] = Field(
        description="List of indices of cards to rearrange in hand",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional reasoning for the decision",
    )


# TODO: Build some tools eg:
# score_hand - scores a proposed hand based on the current game state
# list_resources - list game playing resources
# balatro_wiki - tool for reading the balatro wiki - https://balatrogame.fandom.com/wiki/Balatro_Wiki
# ????

T = TypeVar("T", bound=BaseModel)

SYSTEM_PROMPT = """
You are a strategic card game bot, you are playing the game Balatro.

Your task is to analyze the game state and make decisions based on the current situation.
Describe your reasoning for each decision you make. You can leave notes for yourself in the reasoning field.

You will receive the current game state and must respond in JSON format that matches the provided schema.
You must not include any explanations, markdown code blocks, or additional text in your response.
Your entire response should be parseable as JSON starting with { and ending with }.
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

        game_string = json.dumps(
            self.G,
        )

        try:
            response = llm_model.prompt(
                f"""
{prompt}

Game state:
```json
{game_string}
```

Previous reasoning:
{self.last_reasoning or "No previous reasoning."}

IMPORTANT: You must respond with ONLY a valid JSON object that matches the provided schema.

Schema:
```json
{Schema.model_json_schema()}
```
""",
                system=SYSTEM_PROMPT,
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
            raise RuntimeError(f"Error querying LLM: {e}")

    def skip_or_select_blind(self) -> SkipOrSelectBlindAction:
        """Decide whether to skip or select a blind based on the game state."""
        model: SkipOrSelectBlindModel = self._query_llm(
            prompt="Decide whether to skip or select a blind.",
            Schema=SkipOrSelectBlindModel,
        )
        return (Actions[model.action],)

    def select_cards_from_hand(self) -> SelectCardsFromHandAction:
        model: SelectCardsFromHandModel = self._query_llm(
            prompt="Decide whether to play a hand or discard cards.",
            Schema=SelectCardsFromHandModel,
        )
        return (Actions[model.action], make_one_based(model.indices))

    def select_shop_action(self) -> ShopAction:
        model: ShopActionModel = self._query_llm(
            prompt="Decide whether to buy jokers, boosters or vouchers in the shop.",
            Schema=ShopActionModel,
        )
        if model.indices is None:
            # If no indices are provided, it means the action does not require any specific cards
            return (Actions[model.action],)
        return (Actions[model.action], make_one_based(model.indices))

    def select_booster_action(self) -> BoosterAction:
        """Decide whether to select a card from the booster pack or skip it."""
        model: BoosterActionModel = self._query_llm(
            prompt="Decide whether to select a card from the booster pack or skip it.",
            Schema=BoosterActionModel,
        )
        return (Actions[model.action], make_one_based(model.indices))

    def sell_jokers(self) -> SellJokerAction:
        # Skip for now
        return (Actions.SELL_JOKER, [])

        # if not self.G.get("jokers"):
        #     # If there are no jokers, skip this action
        #     return (Actions.SELL_JOKER, [])

        # model: SellJokerModel = self._query_llm(
        #     prompt="Decide whether to sell jokers.",
        #     Schema=SellJokerModel,
        # )
        # return (Actions[model.action], make_one_based(model.indices))

    def rearrange_jokers(self) -> RearrangeJokersAction:
        """Decide how to rearrange jokers in hand."""
        # if not self.G.get("jokers"):
        #     # If there are no jokers, skip this action

        # Skip for now
        return (Actions.REARRANGE_JOKERS, [])

        # model: RearrangeJokersModel = self._query_llm(
        #     prompt="Decide how to rearrange jokers in hand.",
        #     Schema=RearrangeJokersModel,
        # )
        # return (Actions[model.action], make_one_based(model.indices))

    def use_or_sell_consumables(self) -> UseOrSellConsumablesAction:
        if not self.G.get("consumables"):
            # If there are no consumables, skip this action
            return (Actions.USE_CONSUMABLE, [])

        model: UseOrSellConsumablesModel = self._query_llm(
            prompt="Decide whether to use or sell consumables.",
            Schema=UseOrSellConsumablesModel,
        )
        return (Actions[model.action], make_one_based(model.indices))

    def rearrange_consumables(self) -> RearrangeConsumablesAction:
        # Skip this for now
        # model: RearrangeConsumablesModel = self._query_llm(
        #     prompt="Decide how to rearrange consumables in hand.",
        #     Schema=RearrangeConsumablesModel,
        # )
        return (Actions.REARRANGE_CONSUMABLES, [])

    def rearrange_hand(self) -> RearrangeHandAction:
        """Decide how to rearrange cards in hand."""
        # Skip this for now
        # model: RearrangeHandModel = self._query_llm(
        #     prompt="Decide how to rearrange cards in hand.",
        #     Schema=RearrangeHandModel,
        # )
        return (Actions.REARRANGE_HAND, [])


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
    mybot = LLMBot(
        deck="Blue Deck", stake=1, seed="spicy", challenge=None, bot_port=12347
    )

    # mybot.start_balatro_instance()
    time.sleep(1)

    mybot.run_step()
    mybot.run()
