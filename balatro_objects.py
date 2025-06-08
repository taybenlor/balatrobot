import heapq
from enum import Enum, IntEnum
from collections import Counter
from itertools import combinations



class Hand:
    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        return f'The hand contains {len(self.cards)} cards, with values {[card.card_key for card in self.cards]}'

    def suit_check(self, include_debuffed_cards=False):
        # I know I should just be using the Counter object, sue me!
        if include_debuffed_cards:
            counter = Counter(card.suit for card in self.cards)
        else:
            counter = Counter(card.suit for card in self.cards if not card.debuff)
        # Always ensure our counter has all 4 suits.
        for suit in CardSuits:
            counter.setdefault(suit.value, 0)
        return dict(counter)
    
    def value_check(self, include_debuffed_cards=True):
        # I know I should just be using the Counter object, sue me again!
        if include_debuffed_cards:
            return dict(Counter(card.value for card in self.cards))
        return dict(Counter(card.value for card in self.cards if not card.debuff))

    def get_cards_in_suit(self, suit=None):
        # will always return highest values first
        filtered_cards = [card for card in self.cards if card.suit == suit]
        return sorted(filtered_cards, key=lambda card: card.get_card_ranking(), reverse=True)

    def get_cards_with_value(self, value=None):
        filtered_cards = [card for card in self.cards if card.value == value]
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
        possible_hands = []
        for five_cards in combinations(self.cards, 5):
            suits = {card.suit for card in five_cards}
            values = {card.value for card in five_cards}
            # TODO: let's confirm how we determine values here!
            if len(suits) == 1 and values == []:
                print("I can play a Straight Flush!")
                possible_hands.append(five_cards)
        if len(possible_hands) > 0:
            # TODO: let's return the highest straight flush
            return possible_hands[0]
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
        groups_of_three = sum(1 for count in value_count.values() if count >= 3)
        groups_of_two = sum(1 for count in value_count.values() if count >= 2)
        print("Groups of three: {}".format(groups_of_three))
        print("Groups of two: {}".format(groups_of_two))
        if groups_of_three >= 1 and groups_of_two >= 2:
            # We have the components of a full house.
            print("I can play a Full House!")
            if groups_of_three >= 2:
                print("We have at least two groups of three of a kind, easy pasy!")
                cards = self.get_most_common_cards(value_count=value_count)
                # we will potentially get >5 cards back via this function
                # let's cut this down to only 5 cards
                return [card.index for card in cards[:5]]
            else:
                # We have to get our initial group of 3 cards, then find whatever groups of two we have
                # and selected the highest group of two, and combine with the initial 3
                print("We need to combine a three and a two!")
                first_group_cards = self.get_three_of_a_kind()
                print("First group of cards: {}".format(first_group_cards))
                second_most_common_frequency = heapq.nlargest(2, value_count.values())[1]
                second_most_common_values = [value for value, count in value_count.items() if count == second_most_common_frequency]
                second_group_cards = []
                for value in second_most_common_values:
                    second_group_cards.extend(self.get_cards_with_value(value=value))
                    second_group_cards.sort(key=lambda card: card.get_card_ranking(), reverse=True)
                print("Second group of cards: {}".format(second_group_cards))
                return first_group_cards.extend([card.index for card in second_group_cards[:2]])
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
        # TODO: Determine what the highest straight would be, rather than just returning
        # a response the first time we find something that matches our conditional.
        # TODO: Fix - this doesn't work!
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
    def __init__(self, suit, label, value, name, debuff, card_key, index):
        # Balatro game specific
        self.suit = suit
        self.label = label
        self.value = value
        self.name = name
        self.debuff = debuff
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

class CardSuits(Enum):
    CLUBS = "Clubs"
    SPADES = "Spades"
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"