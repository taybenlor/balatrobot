from enum import IntEnum
from collections import Counter


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        return f'The hand contains {len(self.cards)} cards, with values {[card.card_key for card in self.cards]}'

    def suit_check(self):
        return dict(Counter(card.suit for card in self.cards))
    
    def value_check(self):
        return dict(Counter(card.value for card in self.cards))

    def get_cards_in_suit(self, suit=None):
        # will always return highest values first
        filtered_cards = [card for card in self.cards if card.suit == suit]
        print("Filtered suit cards: {}".format(filtered_cards))
        return sorted(filtered_cards, key=lambda card: card.get_card_ranking())

    def get_cards_with_value(self, value=None):
        filtered_cards = [card for card in self.cards if card.value == value]
        print("Filtered value cards: {}".format(filtered_cards))
        # TODO: How do we sort based on the best value modification approach?
        return sorted(filtered_cards, key=lambda card: card.get_card_ranking())

    # Are hands playable (in order of their poker ranking)
    def get_royal_flush(self):
        # TODO here.
        return []

    def get_straight_flush(self):
        # TODO here.
        return []

    def get_four_of_a_kind(self):
        # are there one or more groups of 4 or more same cards?
        if any(count >= 4 for count in self.value_check().values()):
            return []
        return []

    def get_full_house(self):
        # are there one or more groups of 3 or more cards?
        # are there one or more groups of 2 or more cards? (including the group from above)
        if any(count >= 3 for count in self.value_check().values()) and sum(1 for count in self.value_check().values() if count >= 2) >= 2:
            return []
        return []

    def get_flush(self):
        suit_count = self.suit_check()
        if any(count >= 5 for count in suit_count.values()):
            most_common_suit = max(suit_count, key=suit_count.get)
            print("Most Common Suit: {}".format(most_common_suit))
            # TODO: What happens if we have two suits with the same number of cards?
            cards = self.get_cards_in_suit(suit=most_common_suit)
            return [card.index for card in cards[:5]]
        return []

    def get_straight(self):
        # fuck, how do we do this, using ordering maybe?
        # Big TODO here.
        return []
    
    def get_three_of_a_kind(self):
        if any(count >= 3 for count in self.value_check().values()):
            return []
        return []
    
    def get_two_pair(self):
        if sum(1 for count in self.value_check().values() if count >= 2) >= 2:
            return []
        return []
    
    def get_pair(self):
        value_count = self.value_check()
        if any(count >= 2 for count in value_count.values()):
            most_common_value = max(value_count, key=value_count.get)
            print("Most Common Value: {}".format(most_common_value))
            cards = self.get_cards_with_value(value=most_common_value)
            return [card.index for card in cards]
        return []


class Card:
    def __init__(self, suit, label, value, name, card_key, index):
        # Balatro game specific
        self.suit = suit
        self.label = label
        self.value = value
        self.name = name
        self.card_key = card_key
        # Custom
        # Represents index in current hand
        self.index = index

    def __str__(self):
        return f'This card is the {self.name}. It is in position {self.index} within the hand.'
    
    def __repr__(self):
        return f'Card(\'{self.suit}\', {self.label}, {self.value}, {self.name}, {self.card_key}, {self.index})'

    def get_card_ranking(self):
        if len(self.value) > 2:
            # This is just a named card
            return CardRankings[self.value.upper()]
        else:
            mapping = {
                '10': CardRankings.TEN,
                '9': CardRankings.NINE,
                '8': CardRankings.EIGHT,
                '7': CardRankings.SEVEN,
                '6': CardRankings.SIX,
                '5': CardRankings.FIVE,
                '4': CardRankings.FOUR,
                '3': CardRankings.THREE,
                '2': CardRankings.TWO,
                '1': CardRankings.ONE
            }
            return mapping[self.value]

class CardRankings(IntEnum):
    ACE = 14
    KING = 13
    QUEEN = 12
    JACK = 11
    TEN = 10
    NINE = 9
    EIGHT = 8
    SEVEN = 7
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2
    ONE = 1