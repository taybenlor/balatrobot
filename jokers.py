from collections import defaultdict


jokers_dict = defaultdict(lambda: "missing")
jokers_dict.update(
    {
        "Joker": "+4 Mult",
        "Chaos the Clown": "1 free Reroll per shop",
        "Jolly Joker": "+8 Mult if played hand contains a Pair",
        "Zany Joker": "+12 Mult if played hand contains a Three of a Kind",
        "Mad Joker": "+10 Mult if played hand contains a Two Pair",
        "Crazy Joker": "+12 Mult if played hand contains a Straight",
        "Droll Joker": "+10 Mult if played hand contains a Flush",
        "Half Joker": "+20 Mult if played hand contains 3 or fewer cards",
        "Merry Andy": "+3 discards, -1 hand size",
        "Stone Joker": "This Joker gains +25 Chips for each Stone Card in your full deck ",
        "Juggler": "+1 hand size",
        "Drunkard": "+1 discard",
        "Acrobat": "X3 Mult on final hand of round ",
        "Sock and Buskin": "Retrigger all played face cards",
        "Mime": "Retrigger all card held in hand abilities",
        "Credit Card": "Go up to -$20 in debt",
        "Greedy Joker": "Played cards with Diamond suit give +3 Mult when scored",
        "Lusty Joker": "Played cards with Heart suit give +3 Mult when scored",
        "Wrathful Joker": "Played cards with Spade suit give +3 Mult when scored",
        "Gluttonous Joker": "Played cards with Club suit give +3 Mult when scored",
        "Troubadour": "+2 hand size, -1 hands per round",
        "Banner": "+30 Chips for each remaining discard ",
        "Mystic Summit": "+15 Mult when 0 discards remaining ",
        "Marble Joker": "Adds one Stone card to deck when Blind is selected",
        "Loyalty Card": "X4 Mult every 6 hands played (0 remaining)",
        "Hack": "Retrigger each played 2, 3, 4, or 5",
        "Misprint": "+0 - +23 Mult",
        "Steel Joker": "This Joker gains X0.2 Mult for each Steel Card in your full deck ",
        "Raised Fist": "Adds double the rank of lowest card held in hand to Mult",
        "Golden Joker": "Earn $4 at end of round",
        "Blueprint": "Copies ability of Joker to the right",
        "Glass Joker": "This Joker gains X0.75 Mult for every Glass Card that is destroyed ",
        "Scary Face": "Played face cards give +30 Chips when scored",
        "Abstract Joker": "+3 Mult for each Joker card ",
        "Delayed Gratification": "Earn $2 per discard if no discards are used by end of the round",
        "Golden Ticket": "Played Gold cards earn $4 when scored",
        "Pareidolia": "All cards are considered Face cards",
        "Cartomancer": "Create a Tarot card when Blind is selected (Must have room)",
        "Even Steven": "Played cards with even rank give +4 Mult when scored (10, 8, 6, 4, 2)",
        "Odd Todd": "Played cards with odd rank give +31 Chips when scored (A, 9, 7, 5, 3)",
        "Wee Joker": "This Joker gains +8 Chips when each played 2 is scored ",
        "Business Card": "Played Face cards have a 1 in 2 chance to give $2 when scored",
        "Supernova": "Adds the number of times poker hand has been played to Mult ",
        "Mr. Bones": "Prevents Death if chips scored are at least 25% of required chips self destructs",
        "Seeing Double": "X2 Mult if played hand has a scoring Club card and a scoring card of any other suit",
        "The Duo": "X2 Mult if played hand contains a Pair",
        "The Trio": "X3 Mult if played hand contains a Three of a Kind",
        "The Family": "X4 Mult if played hand contains a Four of a Kind",
        "The Order": "X3 Mult if played hand contains a Straight",
        "The Tribe": "X2 Mult if played hand contains a Flush",
        "8 Ball": "1 in 4 chance for each played 8 to create a Tarot card when scored (Must have room)",
        "Fibonacci": "Each plaed Ace, 2, 3, 5, or 8 gives +8 Mult when scored",
        "Joker Stencil": "X1 Mult for each empty Joker slot Joker stencil included ",
        "Space Joker": "1 in 4 chane to upgrade level of played poker hand",
        "Matador": "Earn $8 if played hand triggers the Boss Blind ability",
        "Ceremonial Dagger": "When Blind is selected, destroy Joker to the right and permanently add double its sell value to this Mult ",
        "Showman": "Joker, Tarot, Planet, and Spectral cards may appear multiple times",
        "Fortune Teller": "+1 Mult per Tarot card used this run ",
        "Hit the Road": "This Joker gains X0.5 Mult per discarded Jack this round ",
        "Swashbuckler": "Adds the sell value of all other owned Jokers to Mult",
        "Flower Pot": "X3 Mult if poker hand contains a Diamond card, Club card, Heart card, and Spade card",
        "Ride the Bus": "This Joker gains +1 Mult per consecutive hand played without a scoring face card ",
        "Shoot the Moon": "+13 Mult for each Queen held in hand",
        "Scholar": "Played Aces give +20 Chips and +4 Mult when scored",
        "Smeared Joker": "Heart and Diamond count as the same suit, Spade and Club count as the same suit",
        "Oops! All 6s": "Double all listed probabilities (ex: 1 in 3 -> 2 in 3)",
        "Four Fingers": "All Flushes and Straights can be made with 4 cards",
        "Gros Michel": "+15 Mult 1 in 6 chance this card is destroyed at the end of the round",
        "Stuntman": "+250 Chips, -2 hand size",
        "Hanging Chad": "Retrigger first played card used in scoring 2 additional times",
        "Driver's License": "X3 Mult if you have at least 16 Enhanced cards in your full deck ",
        "Invisible Joker": "After 2 rounds, sell this card to duplicate a random Joker ",
        "Astronomer": "All Planet cards and Celestial Packs in the shop are free",
        "Burnt Joker": "Upgrade the level of the first discarded poker hand each round",
        "Dusk": "Retrigger all played cards in final hand of round ",
        "Throwback": "X0.25 Mult for each Blind skipped this run ",
        "The Idol": "Each played 2 of Hearts gives X2 Mult when scored Card changes every round",
        "Brainstorm": "Copies the ability of the leftmost Joker",
        "Satellite": "Earn $1 at the end of round per unique Planet card used this run ",
        "Rough Gem": "Played cards with Diamond suit earn $1 when scored",
        "Bloodstone": "1 in 2 chance for played cards with Heart suit to give X1.5 Mult when scored",
        "Arrowhead": "Played cards with Spade suit give +50 Chips when scored",
        "Onyx Agate": "Played cards with Club suit give +7 Mult when scored",
        "Canio": "Gains X1 Mult when a face card is destroyed ",
        "Triboulet": "Played Kings and Queens each give X2 Mult when scored",
        "Yorick": "This Joker gains X1 Mult every 23 [23] cards discarded ",
        "Chicot": "Disables effect of every Boss Blind",
        "Perkeo": "Creates a Negative copy of 1 random consumable card in your possession at the end of the shop",
        "Certificate": "When round begins, add a random playing card with a random seal to your hand",
        "Bootstraps": "+2 Mult for every $5 you have ",
        "Egg": "Gains $3 of sell value at end of round",
        "Burglar": "When Blind is selected, gain +3 Hands and lose all discards",
        "Blackboard": "X3 Mult if all cards held in hand are Spade or Club",
        "Runner": "Gains +15 Chips if played hand contains a Straight ",
        "Ice Cream": "+100 Chips -5 Chips for every hand played",
        "DNA": "If first hand of round has only 1 card, add a permanent copy to deck and draw it to hand",
        "Splash": "Every  played card counts in scoring",
        "Blue Joker": "+2 Chips for each remaining card in Deck ",
        "Sixth Sense": "If first hand of round is a single 6, destroy it and create a Spectral card (Must have room)",
        "Constellation": "This Joker gains X0.1 Mult per Planet card used ",
        "Hiker": "Every played card permanently gains +5 Chips when scored",
        "Faceless Joker": "Earn $5 if 3 or more face cards are discarded at the same time",
        "Green Joker": "+1 Mult per hand played -1 Mult per discard ",
        "Superposition": "Create a Tarot card if poker hand contains an Ace and a Straight (Must have room)",
        "To Do List": "Earn $4 if poker hand is a Pair, poker hand changes at end of round",
        "Cavendish": "X3 Mult 1 in 1000 chance this card is destroy at end of round",
        "Card Sharp": "X3 Mult if played poker hand has already been played this round ",
        "Red Card": "This Joker gains +3 Mult when any Booster Pack is skipped ",
        "Madness": "When Small Blind or Big Blind is selected, gain X0.5 Mult and destroy a random Joker ",
        "Square Joker": "This Joker gains +4 Chips if played hand has exactly 4 card ",
        "Séance": "If poker hand is a Straight Flush, craeate a random Spectral card (Must have room)",
        "Riff-raff": "When Blind is selected, create 2 Common Jokers (Must have room)",
        "Vampire": "This Joker gains X0.1 Mult per scoring Enhanced card played, removes card Enhancement ",
        "Shortcut": "Allows Straights to be made with gaps of 1 rank (ex: 10 8 6 5 3)",
        "Hologram": "This Joker gains X0.25 Mult  per playing card added to your deck ",
        "Vagabond": "Create a Tarot card if hand is played with $4 or less",
        "Baron": "Each King held in hand gives X1.5 Mult",
        "Cloud 9": "Earn $1 for each 9 in your full deck at end of round ",
        "Rocket": "Earn $1 at end of round. Gains $2 when Boss Blind is defeated",
        "Obelisk": "This Joker gains X0.2 Mult per consecutive hand played without playing your must played poker hand ",
        "Midas Mask": "All played face cards become Gold cards when scored",
        "Luchador": "Sell this card to disable the current Boss Blind",
        "Photograph": "First played face card gives X2 Mult when scored",
        "Gift Card": "Add $1 of sell value to every Joker and Consumable card at end of round",
        "Turtle Bean": "+5 hand size, reduces by 1 every round",
        "Erosion": "+4 Mult for each card below 52 in your full deck ",
        "Reserved Parking": "Each face card held in hand has a 1 in 2 chance to give $1",
        "Mail-In Rebate": "Earn $5 for each discarded 2, rank changes every round",
        "To the Moon": "Earn an extra $1 of interest for every $5 you have at end of round",
        "Hallucination": "1 in 2 chance to create a Tarot card when any Booster Pack is opened (Must have room)",
        "Sly Joker": "+50 Chips if played hand contains a Pair",
        "Wily Joker": "+100 Chips if played hand contains a Three of a Kind",
        "Clever Joker": "+80 Chips if played hand contains a Two Pair",
        "Devious Joker": "+100 Chips if played hand contains a Straight",
        "Crafty Joker": "+80 Chips if played hand contains a Flush",
        "Lucky Cat": "This Joker gains X0.25 Mult each time a Lucky card successfully triggers",
        "Baseball Card": "Uncommon Jokers each give X1.5 Mult",
        "Bull": "+2 Chips for each dollar you have ",
        "Diet Cola": "Sell this card to create a free Double Tag",
        "Trading Card": "If first discard of round has only 1 card, destroy it and earn $3",
        "Flash Card": "This Joker gains +2 Mult per reroll in the shop",
        "Popcorn": "+20 Mult -4 Mult per round played",
        "Ramen": "X2 Mult, loses X0.01 Mult per card discarded",
        "Seltzer": "Retrigger all cards played for the next 10 hands",
        "Spare Trousers": "Gain +2 Mult if played hand contains a Two Pair",
        "Campfire": "This Joker gains X0.25 Mult for each card sold, resets when Boss Blind is defeated",
        "Smiley Face": "Played face cards give +5 Mult when scored",
        "Ancient Joker": "Each played card with Heart suit gives X1.5 Mult when scored suit changes at end of round",
        "Walkie Talkie": "Each played 10 or 4 gives +10 Chips and +4 Mult when scored",
        "Castle": "This Joker gains +3 Chips per discarded Heart card, suit changes every round",
    }
)


poker_hand_scoring = """
| Base Scoring           | Poker Hand         | How to Play the Hand                                                                 | Example Cards                |
|------------------------|--------------------|--------------------------------------------------------------------------------------|------------------------------|
| **5 Chips × 1 Mult**   | High Card          | When no other hand is possible, the one highest card in your hand. Aces are high.    | A♠, Q♦, 9♦, 4♣, 3♦           |
| **10 Chips × 2 Mult**  | Pair               | Two cards with a matching rank. Suits may differ.                                    | K♠, 9♠, 9♦, 6♥, 3♦           |
| **20 Chips × 2 Mult**  | Two Pair           | Two cards with a matching rank, and two cards with any other matching rank.          | A♥, A♦, Q♣, 4♥, 4♣           |
| **30 Chips × 3 Mult**  | Three of a Kind    | Three cards with a matching rank. Suits may differ.                                  | 10♠, 10♣, 10♦, 6♥, 5♦        |
| **30 Chips × 4 Mult**  | Straight           | Five cards in consecutive order, not all from the same suit. Aces high or low.       | J♦, 10♣, 9♣, 8♠, 7♥          |
| **35 Chips × 4 Mult**  | Flush              | Five cards of any rank, all from a single suit.                                      | A♥, K♥, 10♥, 5♥, 4♥          |
| **40 Chips × 4 Mult**  | Full House         | Three cards with a matching rank, and two cards with any other matching rank.        | K♥, K♣, K♦, 2♠, 2♦           |
| **60 Chips × 7 Mult**  | Four of a Kind     | Four cards with a matching rank. Suits may differ.                                   | J♠, J♥, J♣, J♦, 3♣           |
| **100 Chips × 8 Mult** | Straight Flush     | Five cards in consecutive order, all from a single suit.                             | Q♠, J♠, 10♠, 9♠, 8♠          |
| **100 Chips × 8 Mult** | Royal Flush        | Ace-high Straight Flush: A, K, Q, J, 10 of the same suit.                            | A♣, K♣, Q♣, J♣, 10♣          |
"""

secret_hand_scoring = """
| Base Scoring           | Poker Hand      | How to Play the Hand                                                                 | Example Cards                |
|------------------------|-----------------|--------------------------------------------------------------------------------------|------------------------------|
| **120 Chips × 12 Mult**| Five of a Kind  | Five cards with the same rank which are not all the same suit.                       | A♠, A♥, A♥, A♣, A♦           |
| **140 Chips × 14 Mult**| Flush House     | Three cards with the same rank, and two cards with the same rank, all from a single suit. | 7♦, 7♦, 7♦, 4♦, 4♦           |
| **160 Chips × 16 Mult**| Flush Five      | Five cards with the same rank and same suit.                                         | A♠, A♠, A♠, A♠, A♠           |
"""

scoring_rules = """
# Scoring Rules for Balatro
## Basic Scoring table

{poker_hand_scoring}

### Held-in-Hand Effects
- Applies to cards in your hand, scored or not.
- Effects include:
    - Steel-enhanced cards (×1.5 mult)
    - Baron joker (mult from Kings)
    - Shoot the Moon (mult from Queens)
    - Reserved Parking ($ chance from face cards)
    - Raised Fist (mult from lowest-ranked card)
- Red Seals trigger these effects twice.
- “The Hook” discards your hand before evaluation, disabling held effects.
- Debuffed cards do not trigger held effects.

### Joker Effects
- Evaluated left to right.
- Jokers give +chips, +mult, or ×mult, based on their conditions.
- Effects can be modified by Joker enhancements:
    - Foil: +50 chips
    - Holographic: +10 mult
    - Polychrome: ×1.5 mult
- Order matters when:
    - Using Blueprint/Brainstorm
    - Combining +mult and ×mult jokers (always put ×mult to the right for maximum effect)
- Upgradeable jokers trigger upgrades before giving effect.
- Degrading jokers (e.g., Ice Cream) apply effect before degrading.

### Secret Poker Hands
There are three "secret" Poker Hands that are only possible through adding cards to your deck, or changing existing cards with Consumables or Jokers.

{secret_hand_scoring}
"""

shop_strategy = """
## Key Strategies for the Shop
*Prioritize Synergy*: Look for Jokers that work well together. For example, a Joker that boosts chips based on discards is excellent for a discard-heavy build. A Joker that boosts multipliers based on hand type is great if you're focusing on a specific hand like straights or flushes.
*Balance Jokers*: Aim for a mix of Jokers that provide chip boosts, multiplier boosts, and multiplier scaling (xMult). A deck with only one type of Joker can be less effective in the long run.
*Consider Hand Types*: Choose a hand type (e.g., flush, full house) and build your deck around it. This allows for more focused strategy and easier scaling with Planet and Tarot cards.
*Don't Overlook Vouchers*: Vouchers provide permanent upgrades, so keep an eye out for them in the shop after defeating bosses. Some vouchers offer significant discounts, so plan your purchases accordingly.
*Be Mindful of Blinds*: Check the upcoming blinds, especially boss blinds, to anticipate their abilities and adjust your deck accordingly.
*Reroll Strategically*: Don't be afraid to reroll the shop, especially if you have a good amount of gold and a specific Joker in mind. Rerolls become more expensive with each use, but reset after each round.
*Utilize Tarot Cards*: Tarot cards can be powerful tools for deck manipulation, allowing you to add, remove, or modify cards. They can be crucial for tailoring your deck to your chosen strategy.
*Consider Skipping Blinds*: If you can afford to skip a blind, you can potentially save money for the next shop visit and earn more interest on your gold, which can be used for future upgrades.
*Economy Matters*: Keep an eye on your gold and try to maximize interest by saving. This will allow you to purchase more upgrades in the shop.
"""

blinds_table = """
| Blind         | Description                                                                                                   | Minimum Ante | Score at least... | ...to earn... |
|---------------|---------------------------------------------------------------------------------------------------------------|--------------|-------------------|---------------|
| Small Blind   | No special effects - can be skipped to receive a Tag                                                          | 1            | 1x base           | $3            |
| Big Blind     | No special effects - can be skipped to receive a Tag                                                          | 1            | 1.5x base         | $4            |
| **Boss Blinds** |                                                                                                               |              |                   |               |
| The Hook      | Discards 2 random cards held in hand after every played hand                                                  | 1            | 2x base           | $5            |
| The Ox        | Playing your most played hand this run sets money to $0                                                       | 6            | 2x base           | $5            |
| The House     | First hand is drawn face down                                                                                  | 2            | 2x base           | $5            |
| The Wall      | Extra large blind                                                                                             | 2            | 4x base           | $5            |
| The Wheel     | 1 in 7 cards get drawn face down during the round                                                             | 2            | 2x base           | $5            |
| The Arm       | Decrease level of played poker hand by 1 (hand levels can go as low as Level 1, and are reduced before scoring)| 2            | 2x base           | $5            |
| The Club      | All Club cards are debuffed                                                                                   | 1            | 2x base           | $5            |
| The Fish      | Cards drawn face down after each hand played                                                                  | 2            | 2x base           | $5            |
| The Psychic   | Must play 5 cards (not all cards need to score)                                                               | 1            | 2x base           | $5            |
| The Goad      | All Spade cards are debuffed                                                                                  | 1            | 2x base           | $5            |
| The Water     | Start with 0 discards                                                                                         | 2            | 2x base           | $5            |
| The Window    | All Diamond cards are debuffed                                                                                | 1            | 2x base           | $5            |
| The Manacle   | -1 Hand Size                                                                                                  | 1            | 2x base           | $5            |
| The Eye       | No repeat hand types this round (every hand played this round must be of a different type and not previously played this round) | 3 | 2x base | $5 |
| The Mouth     | Only one hand type can be played this round                                                                   | 2            | 2x base           | $5            |
| The Plant     | All face cards are debuffed                                                                                   | 4            | 2x base           | $5            |
| The Serpent   | After Play or Discard, always draw 3 cards (ignores hand size)                                                | 5            | 2x base           | $5            |
| The Pillar    | Cards played previously this Ante (during Small and Big Blinds) are debuffed                                  | 1            | 2x base           | $5            |
| The Needle    | Play only 1 hand                                                                                              | 2            | 1x base           | $5            |
| The Head      | All Heart cards are debuffed                                                                                  | 1            | 2x base           | $5            |
| The Tooth     | Lose $1 per card played                                                                                       | 3            | 2x base           | $5            |
| The Flint     | Base Chips and Mult for played poker hands are halved for the entire round                                    | 2            | 2x base           | $5            |
| The Mark      | All face cards are drawn face down                                                                            | 2            | 2x base           | $5            |
| **Finisher Boss Blinds** | (only appearing at Ante 8, 16, etc.)                                                               |              |                   |               |
| Amber Acorn   | Flips and shuffles all Joker cards                                                                            | 8            | 2x base           | $8            |
| Verdant Leaf  | All cards debuffed until 1 Joker sold                                                                         | 8            | 2x base           | $8            |
| Violet Vessel | Very large blind                                                                                              | 8            | 6x base           | $8            |
| Crimson Heart | One random Joker disabled every hand (changes every hand)                                                     | 8            | 2x base           | $8            |
| Cerulean Bell | Forces 1 card to always be selected                                                                           | 8            | 2x base           | $8            |
"""

blinds_dict = {
    "Small Blind": {
        "description": "No special effects - can be skipped to receive a Tag",
        "minimum_ante": 1,
        "score_requirement": "1x",
        "reward": "$3",
    },
    "Big Blind": {
        "description": "No special effects - can be skipped to receive a Tag",
        "minimum_ante": 1,
        "score_requirement": "1.5x",
        "reward": "$4",
    },
    "The Hook": {
        "description": "Discards 2 random cards held in hand after every played hand",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Ox": {
        "description": "Playing your most played hand this run sets money to $0",
        "minimum_ante": 6,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The House": {
        "description": "First hand is drawn face down",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Wall": {
        "description": "Extra large blind",
        "minimum_ante": 2,
        "score_requirement": "4x ",
        "reward": "$5",
    },
    "The Wheel": {
        "description": "1 in 7 cards get drawn face down during the round",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Arm": {
        "description": "Decrease level of played poker hand by 1 (hand levels can go as low as Level 1, and are reduced before scoring)",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Club": {
        "description": "All Club cards are debuffed",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Fish": {
        "description": "Cards drawn face down after each hand played",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Psychic": {
        "description": "Must play 5 cards (not all cards need to score)",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Goad": {
        "description": "All Spade cards are debuffed",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Water": {
        "description": "Start with 0 discards",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Window": {
        "description": "All Diamond cards are debuffed",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Manacle": {
        "description": "-1 Hand Size",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Eye": {
        "description": "No repeat hand types this round (every hand played this round must be of a different type and not previously played this round)",
        "minimum_ante": 3,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Mouth": {
        "description": "Only one hand type can be played this round",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Plant": {
        "description": "All face cards are debuffed",
        "minimum_ante": 4,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Serpent": {
        "description": "After Play or Discard, always draw 3 cards (ignores hand size)",
        "minimum_ante": 5,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Pillar": {
        "description": "Cards played previously this Ante (during Small and Big Blinds) are debuffed",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Needle": {
        "description": "Play only 1 hand",
        "minimum_ante": 2,
        "score_requirement": "1x ",
        "reward": "$5",
    },
    "The Head": {
        "description": "All Heart cards are debuffed",
        "minimum_ante": 1,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Tooth": {
        "description": "Lose $1 per card played",
        "minimum_ante": 3,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Flint": {
        "description": "Base Chips and Mult for played poker hands are halved for the entire round",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "The Mark": {
        "description": "All face cards are drawn face down",
        "minimum_ante": 2,
        "score_requirement": "2x ",
        "reward": "$5",
    },
    "Amber Acorn": {
        "description": "Flips and shuffles all Joker cards",
        "minimum_ante": 8,
        "score_requirement": "2x ",
        "reward": "$8",
    },
    "Verdant Leaf": {
        "description": "All cards debuffed until 1 Joker sold",
        "minimum_ante": 8,
        "score_requirement": "2x ",
        "reward": "$8",
    },
    "Violet Vessel": {
        "description": "Very large blind",
        "minimum_ante": 8,
        "score_requirement": "6x ",
        "reward": "$8",
    },
    "Crimson Heart": {
        "description": "One random Joker disabled every hand (changes every hand)",
        "minimum_ante": 8,
        "score_requirement": "2x ",
        "reward": "$8",
    },
    "Cerulean Bell": {
        "description": "Forces 1 card to always be selected",
        "minimum_ante": 8,
        "score_requirement": "2x ",
        "reward": "$8",
    },
}
