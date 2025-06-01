from enum import IntEnum
from collections import Counter
from itertools import combinations


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        return f'The hand contains {len(self.cards)} cards, with values {[card.card_key for card in self.cards]}'

    def suit_check(self):
        # I know I should just be using the Counter object, sue me!
        return dict(Counter(card.suit for card in self.cards))
    
    def value_check(self):
        # I know I should just be using the Counter object, sue me again!
        return dict(Counter(card.value for card in self.cards))

    def get_cards_in_suit(self, suit=None):
        # will always return highest values first
        filtered_cards = [card for card in self.cards if card.suit == suit]
        # print("Filtered suit cards: {}".format(filtered_cards))
        return sorted(filtered_cards, key=lambda card: card.get_card_ranking(), reverse=True)

    def get_cards_with_value(self, value=None):
        filtered_cards = [card for card in self.cards if card.value == value]
        # print("Filtered value cards: {}".format(filtered_cards))
        # TODO: How do we sort based on the best value modification approach?
        return sorted(filtered_cards, key=lambda card: card.get_card_ranking(), reverse=True)
    
    def get_most_common_cards(self, value_count={}):
        # By calling this, we're assuming there is one card value that
        # has a higher count compared to all others.
        highest_card_frequency = max(value_count.values())
        most_common_values = [value for value, count in value_count.items() if count == highest_card_frequency]
        cards = []
        print("Most Common Values: {}".format(most_common_values))
        for value in most_common_values:
            # TODO: How do we sort based on the best value modification approach?
            cards.extend(self.get_cards_with_value(value=value))
        return cards

    # Are hands playable (in order of their poker ranking)
    def get_royal_flush(self):
        ROYAL_VALUES = {'10', 'J', 'Q', 'K', 'A'}
        for five_cards in combinations(self.cards, 5):
            suits = {card.suit for card in five_cards}
            values = {card.value for card in five_cards}
            if len(suits) == 1 and values == ROYAL_VALUES:
                # By golly, we've actually got one!
                # Fun fact, the odds of getting a royal flush are 1 in 649,739 (with a standard 52 card deck)
                print("I can play a Royal Flush!")
                return [card.index for card in five_cards]
        return []

    def get_straight_flush(self):
        # TODO here.
        # We'll have to combine approaches between royal flush and straight.
        # print("I can play a Straight Flush!")
        return []

    def get_four_of_a_kind(self):
        # are there one or more groups of 4 or more same cards?
        value_count = self.value_check()
        if any(count >= 4 for count in value_count.values()):
            cards = self.get_most_common_cards(value_count=value_count)
            print("I can play Four of a Kind!")
            return [card.index for card in cards]
        return []

    def get_full_house(self):
        # are there one or more groups of 3 or more cards?
        # are there one or more groups of 2 or more cards? (including the group from above)
        value_count = self.value_check()
        if any(count >= 3 for count in value_count.values()) and sum(1 for count in value_count.values() if count >= 2) >= 2:
            first_group = self.get_most_common_cards(value_count=value_count)
            value_count_copy = value_count.copy()
            del value_count_copy[max(value_count, key=value_count.get)]
            second_group = self.get_most_common_cards(value_count=value_count_copy)
            print("I can play a Full House!")
            return [card.index for card in first_group].extend([card.index for card in second_group])
        return []

    def get_flush(self):
        suit_count = self.suit_check()
        if any(count >= 5 for count in suit_count.values()):
            most_common_suit = max(suit_count, key=suit_count.get)
            print("Most Common Suit: {}".format(most_common_suit))
            # TODO: What happens if we have two suits with the same number of cards?
            cards = self.get_cards_in_suit(suit=most_common_suit)
            print("I can play a Flush!")
            return [card.index for card in cards[:5]]
        return []

    def get_straight(self):
        for five_cards in combinations(self.cards, 5):
            values = sorted(card.get_card_ranking() for card in five_cards)
            alt_values = [1 if v == 14 else v for v in values].sort()
            if all(values[i] == values[i - 1] + 1 for i in range(1, 5)) or all(alt_values[i] == alt_values[i - 1] + 1 for i in range(1, 5)):
                print("I can play a Straight!")
                return [card.index for card in five_cards]
        return []
    
    def get_three_of_a_kind(self):
        value_count = self.value_check()
        if any(count >= 3 for count in value_count.values()):
            cards = self.get_most_common_cards(value_count=value_count)
            print("I can play Three of a Kind!")
            return [card.index for card in cards]
        return []
    
    def get_two_pair(self):
        value_count = self.value_check()
        if sum(1 for count in value_count.values() if count >= 2) >= 2:
            cards = self.get_most_common_cards(value_count=value_count)
            print("I can play Two Pair!")
            return [card.index for card in cards]
        return []
    
    def get_pair(self):
        value_count = self.value_check()
        if any(count >= 2 for count in value_count.values()):
            cards = self.get_most_common_cards(value_count=value_count)
            print("I can play a pair!")
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