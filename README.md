# Balatrobot - A Botting API Implementation for Balatro

Forked from https://github.com/besteon/balatrobot

## Installation

Requires Steamodded (Tested on v0.9.3)

## Botting

This is an attempt to create a bot that utilises the Balatrobot API to use a flush-focused strategy to get to the end of round 8 for a basic blue deck.

Look at _flush_strategy.py_ for approach in development.

Current strategy:

**Playing Hands**
- Check hand for a flush or higher, and play if possible.
- If any of those hands cannot be played, discard cards not related to most common suit (and index towards achieving a flush).
- If there are 0 discards available, try and play a hand lower ranked than flush (with additional discards included).
- If there are no valid hands available, play all cards that were going to be discarded.

**Shop Purchasing**
- Based on a ranking system, try and purchase jokers related to flushes, increasing overall multi, chips, or special jokers - in that order.
- Purchase any planet card and use if it is less than 1/3rd of the current available money.
- Purchase specific tarot cards, if they are available and affordable.
- Purchase specific spectral cards, if they are available and affordable.
- Purchase any booster pack, only excluding playing card packs.
- Try to re-roll in the shop if re-roll is free, or if it's less than 1/2 of current available money.
- Always try to purchase the "Clearance Sale" voucher.

**Booster Pack Card Selections**
- Select specific cards if they have been specified as a priority.
- If no priority cards exist in the pack, select the first card that doesn't require cards from the deck to be selected. 

**To Do (a lot):**
- Start taking into consideration boss abilities.
- Take into account card enhancements when determining what cards to play.
- Select tarot and spectral cards in combination with cards in the hand.
- If we get a joker we don't want to continue using, sell it.
- And much more, I'm sure.

## Disclaimer

I'm just messing around with this so I can talk about it. This mod may not even work with your environment, and this mod may not work in conjunction with other mods. Use at your own risk.
