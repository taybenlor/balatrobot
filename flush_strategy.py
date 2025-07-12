import time
import argparse

from utils import delete_game_cache
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
                debuff=card['debuff'],
                card_key=card['card_key'],
                index=index + 1
            )
        )
    hand = Hand(
        cards=cards
    )

    # Is there a flush or better we can play here?
    play_hand = (
        hand.get_royal_flush() if hand.get_royal_flush() else
        hand.get_straight_flush() if hand.get_straight_flush() else
        hand.get_four_of_a_kind() if hand.get_four_of_a_kind() else
        hand.get_full_house() if hand.get_full_house() else
        hand.get_flush() if hand.get_flush() else
        None
    )

    if play_hand:
        # We can play a flush or better hand!
        self.state["hands_played"] += 1
        print("Going to play hand: {}".format(play_hand))
        return [
            Actions.PLAY_HAND,
            play_hand
        ]

    # Okay, we can't play a flush or better, maybe we should try to discard instead!
    # Let's just firstly figure out what we should discard first.
    suit_count = hand.suit_check()
    discard_hand = []
    # We don't want to include the flush suit in our discard, as this goes against the purpose of discarding!
    while len(discard_hand) < 5 and len(suit_count.keys()) > 1:
        least_common_suit = min(suit_count, key=suit_count.get)
        suit_count.pop(least_common_suit)
        # always attach lower valued cards first for discard
        for card in sorted(hand.cards, key=lambda card: card.get_card_ranking()):
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
    # What other basic hands could we play?
    play_hand = (
        hand.get_straight() if hand.get_straight() else
        hand.get_three_of_a_kind() if hand.get_three_of_a_kind() else
        hand.get_two_pair() if hand.get_two_pair() else
        hand.get_pair() if hand.get_pair() else
        []
    )

    # We're going to be playing a hand now whether we like it or not.

    self.state["hands_played"] += 1
    if play_hand and len(play_hand) < 5:
        # We've found an alternative hand to play
        # but we should discard some cards with it
        index = 0
        while len(play_hand) < 5 and index < len(discard_hand):
            if discard_hand[index] not in play_hand:
                play_hand.append(discard_hand[index])
            index += 1
        print("Playing an alternative hand (with discards): {}".format(play_hand))
        return [Actions.PLAY_HAND, list(play_hand)]
    elif play_hand:
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

    # Shop prioritization order:
    # 1 - Jokers
    # 2 - Boosters
    # 3 - Vouchers
    # Except in the case that the "Clearance Sale" (25% off) voucher is available - we should buy this, provided we have a bit of money to spend afterwards

    # look at G["dollars"] - that's our current wallet
    # but also check G["bankrupt_at"] - we might be able to go into debt
    current_dollars = G["dollars"] - G["bankrupt_at"]
    print("I think have have this amount: {}".format(current_dollars))

    # TODO: do we want to immediately sell any jokers in order to make more money?
    # potential_sell_action = self.sell_jokers(self, G)
    # if len(potential_sell_action[1]) > 0:
    #     # we have jokers we want to sell!
    #     return potential_sell_action

    voucher_names = [voucher["label"] for voucher in G["shop"]["vouchers"]]
    if "Clearance Sale" in voucher_names and current_dollars >= 15:
        # this will make things cheaper moving forward
        idx = voucher_names.index("Clearance Sale")
        return [Actions.BUY_VOUCHER, [idx + 1]]

    # let's check jokers
    print("Checking Jokers in Shop!")
    for index, card in enumerate(G["shop"]["cards"]):
        cost = card["cost"]
        label = card["label"]
        card_set = card["ability"]["set"]
        affordable = cost < current_dollars
        print("Looking at card: {}".format(label))
        # default max jokers is 5, but we should increase this number if there
        # are any 'negative' jokers in our joker list
        if card_set == 'Joker' and len(G['jokers']) < 5:
            if label in self.prioritization_config['flush_priority_jokers'] and affordable:
                print("Going to buy Joker: {}!".format(label))
                return [Actions.BUY_CARD, [index + 1]]
            elif label in self.prioritization_config['multi_based_jokers'] and affordable:
                print("Going to buy Joker: {}!".format(label))
                return [Actions.BUY_CARD, [index + 1]]
            elif label in self.prioritization_config['chip_based_jokers'] and affordable:
                print("Going to buy Joker: {}".format(label))
                return [Actions.BUY_CARD, [index + 1]]
            elif label in self.prioritization_config['other_jokers'] and affordable:
                print("Going to buy Joker: {}".format(label))
                return [Actions.BUY_CARD, [index + 1]]
            elif cost == 0:
                print("Going to buy free Joker to sell: {}".format(label))
                return [Actions.BUY_CARD, [index + 1]]
        elif card_set == 'Planet':
            if label in self.prioritization_config['priority_planet_cards'] and affordable:
                print("Going to buy priority planet card: {}".format(label))
                return [Actions.BUY_CARD, [index + 1]]
            elif affordable and cost * 3 < current_dollars:
                print("We have more than enough money for this planet card, we're going to buy it!")
                return [Actions.BUY_CARD, [index + 1]]
        elif card_set == 'Tarot':
            if label in self.prioritization_config['priority_tarot_cards'] and affordable:
                print("Going to buy priority tarot card: {}".format(label))
                return [Actions.BUY_CARD, [index + 1]]
        print("Decided to skip card!")

    # Let's check the booster packs
    for index, booster in enumerate(G["shop"]["boosters"]):
        cost = booster["cost"]
        label = booster["label"]
        affordable = cost < current_dollars
        print("Looking at booster pack: {}".format(label))
        if "Standard" not in label and affordable:
            print("Going to buy booster pack!")
            return [Actions.BUY_BOOSTER, [index + 1]]

    # let's check other vouchers
    for index, voucher in enumerate(G["shop"]["vouchers"]):
        cost = voucher["cost"]
        label = voucher["label"]
        affordable = cost < current_dollars
        if label in self.prioritization_config['priority_vouchers'] and affordable:
            return [Actions.BUY_VOUCHER, [index + 1]]

    if (G["shop"]["reroll_cost"] * 2 < current_dollars) or G["shop"]["reroll_cost"] == 0:
        # We have enough money to do a re-roll
        # Let's see if we can get anything better
        print("Performing re-roll in shop, we have more than double the money of a re-roll!")
        return [Actions.REROLL_SHOP]

    # Nothing else left to do!
    return [Actions.END_SHOP]


def select_booster_action(self, G):

    if G['pack_cards'][0]['ability']['set'] == "Planet":
        maybe_indexes = []
        for index, planet_card in enumerate(G["pack_cards"]):
            if planet_card['label'] in self.prioritization_config['priority_planet_cards']:
                print("Choosing to select a priority planet card!")
                maybe_indexes.append(index+1)
        if maybe_indexes:
            return [Actions.SELECT_BOOSTER_CARD, maybe_indexes, []]
        else:
            print("Choosing to select first 1-2 booster card/s instead!")
            return [Actions.SELECT_BOOSTER_CARD, [1, 2], []]

    if G['pack_cards'][0]['ability']['set'] == "Tarot":
        maybe_indexes = []
        for index, tarot_card in enumerate(G["pack_cards"]):
            if tarot_card['label'] in self.prioritization_config['priority_tarot_cards']:
                print("Choosing to select a priority tarot card!")
                maybe_indexes.append(index+1)
        for index, tarot_card in enumerate(G['pack_cards']):
            if tarot_card['ability'].get('max_highlighted') is None and (tarot_card['label'] == "The Fool" and len(tarot_card['ability']['consumeable']) > 1):
                print("Choosing to select tarot that doesn't need to select cards in the deck - {} at position {}!".format(tarot_card['label'], index+1))
                maybe_indexes.append(index+1)
        if maybe_indexes:
            return [Actions.SELECT_BOOSTER_CARD, maybe_indexes, []]
        else:
            # passing through hand indexes, just in case
            return [Actions.SELECT_BOOSTER_CARD, [1, 2], [1, 2]]

    if G['pack_cards'][0]['ability']['set'] == "Joker" and len(G['jokers']) < 5:
        maybe_indexes = []
        for index, joker in enumerate(G['pack_cards']):
            label = joker['label']
            if label in self.prioritization_config['flush_priority_jokers']:
                print("Going to select Joker: {}!".format(label))
                maybe_indexes.append(index+1)
            elif label in self.prioritization_config['multi_based_jokers']:
                print("Going to select Joker: {}!".format(label))
                maybe_indexes.append(index+1)
            elif label in self.prioritization_config['chip_based_jokers']:
                print("Going to select Joker: {}".format(label))
                maybe_indexes.append(index+1)
            elif label in self.prioritization_config['other_jokers']:
                print("Going to select Joker: {}".format(label))
        if maybe_indexes:
            return [Actions.SELECT_BOOSTER_CARD, maybe_indexes]
        else:
            print("Choosing to select first joker (maybe it will help?)")
            return [Actions.SELECT_BOOSTER_CARD, [1]]

    if G['pack_cards'][0]['ability']['set'] == "Spectral":
        maybe_indexes = []
        for index, spectral_card in enumerate(G['pack_cards']):
            label = spectral_card['label']
            if label in self.prioritization_config['priority_spectral_cards']:
                print('Going to select priority spectral card: {}!'.format(label))
                maybe_indexes.append(index+1)
        for index, spectral_card in enumerate(G['pack_cards']):
            if spectral_card['ability'].get('max_highlighted') is None:
                print("Choosing to select spectral card that doesn't need to select cards in the deck - {} at position {}!".format(spectral_card['label'], index+1))
                maybe_indexes.append(index+1)
        if maybe_indexes:
            return [Actions.SELECT_BOOSTER_CARD, maybe_indexes, [1, 2, 3]]
        else:
            # passing through hand indexes, just in case
            return [Actions.SELECT_BOOSTER_CARD, [1], [1,2,3]]

    print("Choosing to Skip Booster Pack!")
    return [Actions.SKIP_BOOSTER_PACK]


def sell_jokers(self, G):
    # Until I can work out how to trigger this while in the shop, its not worth using.
    # We shouldn't sell jokers at the beginning of choosing a hand.
    # -----
    # main_jokers = self.prioritization_config['flush_priority_jokers'] + self.prioritization_config['multi_based_jokers'] + self.prioritization_config['chip_based_jokers'] + self.prioritization_config['other_jokers']
    # for index, joker in enumerate(G['jokers']):
    #     label = joker["label"]
    #     if label not in main_jokers:
    #         print("We have a joker we want to get rid of - {} at position {}!".format(label, index+1))
    #         return [Actions.SELL_JOKER, [index+1]]
    return [Actions.SELL_JOKER, []]


def rearrange_jokers(self, G):
    # what is the preferred order?
    # 1 - additional chips
    # 2 - additional multi (quantity)
    # 3 - additional multi (multiplier)
    return [Actions.REARRANGE_JOKERS, []]


def use_or_sell_consumables(self, G):
    for index, card in enumerate(G['consumables']):
        if card['ability'].get('max_highlighted') is None:
            print("Choosing to use consumable that doesn't need to be used on select cards in deck - {} at position {}!".format(card['label'], index+1))
            return [Actions.USE_CONSUMABLE, [index+1]]
        else:
            return [Actions.SELL_CONSUMABLE, [index+1]]
    return [Actions.SELL_CONSUMABLE, []]


def rearrange_consumables(self, G):
    return [Actions.REARRANGE_CONSUMABLES, []]


def rearrange_hand(self, G):
    return [Actions.REARRANGE_HAND, []]


if __name__ == "__main__":
    # do we want to delete all our gamestate_cache files and start with a fresh state?
    parser = argparse.ArgumentParser(description="Game cache management script")
    parser.add_argument('--delete-game-cache', action='store_true', help='Delete all .json files in the gamestate_cache directory')
    args = parser.parse_args()

    if args.delete_game_cache:
        delete_game_cache()

    # creating balatro bot
    mybot = Bot(
        deck="Blue Deck",
        stake=1,
        seed=None,
        challenge=None,
        bot_port=12347
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

    # mybot.start_balatro_instance()
    time.sleep(5)

    mybot.run_step()
    mybot.run()
