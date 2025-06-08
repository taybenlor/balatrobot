# Balatrobot - A Botting API Implementation for Balatro

Forked from https://github.com/besteon/balatrobot

## Installation

Requires Steamodded (Tested on v0.9.3)

## Botting

This is an attempt to create a bot that utilises the Balatrobot API to use a flush-focused strategy to get to the end of round 8 for a basic blue deck.

Look at _flush_strategy.py_ for approach in development.

Current strategy:
- Check hand for a flush, and play if possible.
- If a flush cannot be played, discard cards not related to most common suit.
- If there are 0 discards available, try and play a different hand (based on poker ranking).
- If there are no valid hands available, play the cards that were going to be discarded.

To Do (a lot):
- Start taking into consideration boss abilities.
- Select arcane cards from packs (if triggered by skipping a blind)
- Select planet cards from packs (if triggered by skipping a blind)
- Interactions with the store
    - Take into consideration current wallet
    - Buy jokers if they are advantageous to strategy
    - Buy planet packs if possible
        - Apply planet packs in order of relevance for strategy
    - Buy arcane packs if possible
        - Apply planet packs in order of relevant for strategy
- Take into account card enhancements when determining what cards to play
- And much more, I'm sure.

## Disclaimer

I'm just messing around with this so I can talk about it. This mod may not even work with your environment, and this mod may not work in conjunction with other mods. Use at your own risk.
