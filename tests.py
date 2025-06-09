import unittest
from balatro_objects import Hand, Card

class TestHandValidationMethods(unittest.TestCase):

    def test_confirm_pair(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Clubs', label='Base Card', value='King', name='King of Clubs', debuff=False, card_key='C_K', index=2)
        hand = Hand(cards = [card_1, card_2, card_3])
        self.assertEqual(hand.get_pair(), [0,1])

    def test_confirm_two_pair(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Clubs', label='Base Card', value='King', name='King of Clubs', debuff=False, card_key='C_K', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=3)
        card_5 = Card(suit='Hearts', label='Base Card', value='Four', name='Four of Hearts', debuff=False, card_key='H_4', index=4)
        hand = Hand( cards = [card_1, card_2, card_3, card_4, card_5])
        self.assertEqual(hand.get_two_pair(), [0,1,2,3])

    def test_three_of_a_kind(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Spades', label='Base Card', value='Ace', name='Ace of Spades', debuff=False, card_key='S_A', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=3)
        hand = Hand(cards = [card_1, card_2, card_3, card_4])
        self.assertEqual(hand.get_three_of_a_kind(), [0,1,2])

    def test_straight(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='King', name='King of Clubs', debuff=False, card_key='C_K', index=1)
        card_3 = Card(suit='Clubs', label='Base Card', value='Queen', name='Queen of Clubs', debuff=False, card_key='C_Q', index=3)
        card_4 = Card(suit='Hearts', label='Base Card', value='Jack', name='Jack of Hearts', debuff=False, card_key='H_J', index=4)
        card_5 = Card(suit='Hearts', label='Base Card', value='Ten', name='Ten of Hearts', debuff=False, card_key='H_10', index=5)
        card_6 = Card(suit='Clubs', label='Base Card', value='Seven', name='Seven of Clubs', debuff=False, card_key='C_7', index=2)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5, card_6])
        self.assertEqual(hand.get_straight(), [0,1,3,4,5])

    def test_flush(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Five', name='Five of Hearts', debuff=False, card_key='H_5', index=0)
        card_2 = Card(suit='Hearts', label='Base Card', value='Queen', name='Queen of Hearts', debuff=False, card_key='H_Q', index=1)
        card_3 = Card(suit='Hearts', label='Base Card', value='Jack', name='Jack of Hearts', debuff=False, card_key='H_J', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='Ten', name='Ten of Hearts', debuff=False, card_key='H_10', index=3)
        card_5 = Card(suit='Hearts', label='Base Card', value='Nine', name='Nine of Hearts', debuff=False, card_key='H_9', index=4)
        card_6 = Card(suit='Clubs', label='Base Card', value='Seven', name='Seven of Clubs', debuff=False, card_key='C_7', index=5)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5, card_6])
        self.assertEqual(hand.get_flush(), [1,2,3,4,0])

    def test_full_house_v1(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Spades', label='Base Card', value='Ace', name='Ace of Spades', debuff=False, card_key='S_A', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=3)
        card_5 = Card(suit='Spades', label='Base Card', value='King', name='King of Spades', debuff=False, card_key='S_K', index=4)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5])
        self.assertEqual(hand.get_full_house(), [0,1,2,3,4])

    def test_full_house_v2(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Spades', label='Base Card', value='Ace', name='Ace of Spades', debuff=False, card_key='S_A', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=3)
        card_5 = Card(suit='Spades', label='Base Card', value='King', name='King of Spades', debuff=False, card_key='S_K', index=4)
        card_6 = Card(suit='Diamonds', label='Base Card', value='King', name='King of Diamonds', debuff=False, card_key='D_K', index=5)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5, card_6])
        self.assertEqual(hand.get_full_house(), [0,1,2,3,4])

    def test_four_of_a_kind(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Clubs', label='Base Card', value='Ace', name='Ace of Clubs', debuff=False, card_key='C_A', index=1)
        card_3 = Card(suit='Spades', label='Base Card', value='Ace', name='Ace of Spades', debuff=False, card_key='S_A', index=2)
        card_4 = Card(suit='Diamonds', label='Base Card', value='Ace', name='King of Diamonds', debuff=False, card_key='D_K', index=3)
        card_5 = Card(suit='Spades', label='Base Card', value='King', name='King of Spades', debuff=False, card_key='S_K', index=4)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5])
        self.assertEqual(hand.get_four_of_a_kind(), [0,1,2,3])

    def test_straight_flush(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=0)
        card_2 = Card(suit='Hearts', label='Base Card', value='Queen', name='Queen of Hearts', debuff=False, card_key='H_Q', index=1)
        card_3 = Card(suit='Hearts', label='Base Card', value='Jack', name='Jack of Hearts', debuff=False, card_key='H_J', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='Ten', name='Ten of Hearts', debuff=False, card_key='H_10', index=3)
        card_5 = Card(suit='Hearts', label='Base Card', value='Nine', name='Nine of Hearts', debuff=False, card_key='H_9', index=4)
        card_6 = Card(suit='Clubs', label='Base Card', value='Seven', name='Seven of Clubs', debuff=False, card_key='C_7', index=5)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5, card_6])
        self.assertEqual(hand.get_straight_flush(), [0,1,2,3,4])

    def test_royal_flush(self):
        card_1 = Card(suit='Hearts', label='Base Card', value='Ace', name='Ace of Hearts', debuff=False, card_key='H_A', index=0)
        card_2 = Card(suit='Hearts', label='Base Card', value='King', name='King of Hearts', debuff=False, card_key='H_K', index=1)
        card_3 = Card(suit='Hearts', label='Base Card', value='Queen', name='Queen of Hearts', debuff=False, card_key='H_Q', index=2)
        card_4 = Card(suit='Hearts', label='Base Card', value='Jack', name='Jack of Hearts', debuff=False, card_key='H_J', index=3)
        card_5 = Card(suit='Hearts', label='Base Card', value='Ten', name='Ten of Hearts', debuff=False, card_key='H_10', index=4)
        card_6 = Card(suit='Hearts', label='Base Card', value='Nine', name='Nine of Hearts', debuff=False, card_key='H_9', index=5)
        card_7 = Card(suit='Clubs', label='Base Card', value='Seven', name='Seven of Clubs', debuff=False, card_key='C_7', index=6)
        hand = Hand(cards=[card_1, card_2, card_3, card_4, card_5, card_6, card_7])
        self.assertEqual(hand.get_royal_flush(), [0,1,2,3,4])

if __name__ == '__main__':
    unittest.main()