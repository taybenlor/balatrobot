import time
import copy
from bot import Bot, Actions
from balatro_objects import Hand, Card


def skip_or_select_blind(self, G):
    if (
        G["ante"]["blinds"]["ondeck"] == "Small"
        or G["ante"]["blinds"]["ondeck"] == "Big"
    ):
        return [Actions.SKIP_BLIND]
    else:
        return [Actions.SELECT_BLIND]


def select_cards_from_hand(self, G):
    # G["hand"] is a list of cards in the hand

    # Example of playing the first card in the hand
    # return [Actions.PLAY_HAND, [1]]

    # Example of discarding the first card in the hand
    # return [Actions.DISCARD_HAND, [1]]

    # Flush Strategy
    # - Check hand for number of each suit
    # - Based on suit number, is there a flush we can play?
    #     - If yes, play the flush
    #     - If no, continue 
    # - Check deck for number of each suit left available
    # - Discard lowest frequency suits (up to 5 cards)

    # Note:
    # Take into account boss level (are we debuffing a particular suit)

    if "hands_played" not in self.state:
        self.state["hands_played"] = 0

    cards = []
    for index, card in enumerate(G["hand"]):
        cards.append(
            Card(
                suit=card['suit'],
                label=card['label'],
                value=card['value'],
                name=card['name'],
                card_key=card['card_key'],
                index=index + 1
            )
        )
    hand = Hand(
        cards=cards
    )

    # What's the actual hand we're going to play?
    play_hand = None

    if hand.get_flush():
        # We can play a flush!
        self.state["hands_played"] += 1
        play_hand = hand.get_flush()
        print("Going to play hand: {}".format(play_hand))
        return [
            Actions.PLAY_HAND,
            play_hand
        ]
    
    # Okay, we can't play a flush, maybe we should try to discard instead!
    # Let's just firstly figure out what we should discard first.
    suit_count = hand.suit_check()
    discard_hand = []
    # We don't want to include the flush suit in our discard, as this goes against the purpose of discarding!
    while len(discard_hand) < 5 and len(suit_count.keys()) > 1:
        least_common_suit = min(suit_count, key=suit_count.get)
        suit_count.pop(least_common_suit)
        for card in hand.cards:
            if card.suit == least_common_suit and len(discard_hand) < 5:
                discard_hand.append(card.index)
    # If we have discards, let's go with this strategy.
    if G["current_round"]["discards_left"] > 0:
        print("Going to discard hand: {}".format(discard_hand))
        return [
            Actions.DISCARD_HAND,
            discard_hand
        ]

    # We've really screwed the pooch here.
    # We don't have a valid flush to play, but we don't have any discards left either.
    # What other hands could we play?
    play_hand = (
        hand.get_royal_flush() if hand.get_royal_flush() else
        hand.get_straight_flush() if hand.get_straight_flush() else
        hand.get_four_of_a_kind() if hand.get_four_of_a_kind() else
        hand.get_full_house() if hand.get_full_house() else
        hand.get_three_of_a_kind() if hand.get_three_of_a_kind() else
        hand.get_two_pair() if hand.get_two_pair() else
        hand.get_pair() if hand.get_pair() else
        []
    )

    # We're going to be playing a hand now whether we like it or not.

    self.state["hands_played"] += 1
    if play_hand:
        # We've found an alternative hand to play
        print("Playing an alternative hand: {}".format(play_hand))
        return [Actions.PLAY_HAND, play_hand]
    else:
        # We legitimately 
        print("No discards available. Going to play discardable hand: {}".format(discard_hand))
        return [Actions.PLAY_HAND, discard_hand]


def select_shop_action(self, G):
    if "num_shops" not in self.state:
        self.state["num_shops"] = 0

    self.state["num_shops"] += 1

    if self.state["num_shops"] == 1:
        return [Actions.BUY_CARD, [2]]
    elif self.state["num_shops"] == 5:
        return [Actions.BUY_CARD, [2]]

    return [Actions.END_SHOP]


def select_booster_action(self, G):
    return [Actions.SKIP_BOOSTER_PACK]


def sell_jokers(self, G):
    if len(G["jokers"]) > 1:
        return [Actions.SELL_JOKER, [2]]

    return [Actions.SELL_JOKER, []]


def rearrange_jokers(self, G):
    return [Actions.REARRANGE_JOKERS, []]


def use_or_sell_consumables(self, G):
    return [Actions.USE_CONSUMABLE, []]


def rearrange_consumables(self, G):
    return [Actions.REARRANGE_CONSUMABLES, []]


def rearrange_hand(self, G):
    return [Actions.REARRANGE_HAND, []]


if __name__ == "__main__":
    mybot = Bot(
        deck="Blue Deck",
        stake=1,
        seed=None,
        challenge=None,
        bot_port=12345
    )

    mybot.skip_or_select_blind = skip_or_select_blind
    mybot.select_cards_from_hand = select_cards_from_hand
    mybot.select_shop_action = select_shop_action
    mybot.select_booster_action = select_booster_action
    mybot.sell_jokers = sell_jokers
    mybot.rearrange_jokers = rearrange_jokers
    mybot.use_or_sell_consumables = use_or_sell_consumables
    mybot.rearrange_consumables = rearrange_consumables
    mybot.rearrange_hand = rearrange_hand

    mybot.start_balatro_instance()
    time.sleep(20)

    mybot.run_step()
    mybot.run()
