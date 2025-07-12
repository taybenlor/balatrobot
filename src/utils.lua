
Utils = { }

function Utils.getCardData(card)
    local _card = { }

    _card.label = card.label
    _card.cost = card.cost
    _card.debuff = card.debuff
    _card.name = card.config.card.name
    _card.suit = card.config.card.suit
    _card.value = card.config.card.value
    _card.card_key = card.config.card_key

    if card.ability then
        _card.ability = card.ability
    end

    return _card
end

function Utils.getDeckData()
    local _deck = { }

    return _deck
end

function Utils.getHandData()
    local _hand = { }

    if G and G.hand and G.hand.cards then
        for i = 1, #G.hand.cards do
            local _card = Utils.getCardData(G.hand.cards[i])
            _hand[i] = _card
        end
    end

    return _hand
end

function Utils.getPackCardsData()
    local _pack = { }

    if G and G.pack_cards and G.pack_cards.cards then
        for i = 1, #G.pack_cards.cards do
            local _card = Utils.getCardData(G.pack_cards.cards[i])
            _pack[i] = _card
        end
    end

    return _pack
end

function Utils.getJokersData()
    local _jokers = { }

    if G and G.jokers and G.jokers.cards then
        for i = 1, #G.jokers.cards do
            local _card = Utils.getCardData(G.jokers.cards[i])
            _jokers[i] = _card
        end
    end

    return _jokers
end

function Utils.getConsumablesData()
    local _consumables = { }

    if G and G.consumables and G.consumables.cards then
        for i = 1, #G.consumeables.cards do
            local _card = Utils.getCardData(G.consumeables.cards[i])
            _consumables[i] = _card
        end
    end

    return _consumables
end

function Utils.getBlindData()
    local _blinds = {}
    _blinds.skip_tag = {}

    if G and G.GAME then
        _blinds.ondeck = G.GAME.blind_on_deck
    end

    if G and G.GAME and G.GAME.blind and G.GAME.blind.name then
        _blinds.name = G.GAME.blind.name
    end

    if G and G.GAME and G.GAME.round_resets and G.GAME.round_resets.blind_choices and G.GAME.round_resets.blind_choices.Boss then
        _blinds.boss = G.P_BLINDS[G.GAME.round_resets.blind_choices.Boss].name
    end

    if G and G.GAME and G.GAME.round_resets and G.GAME.round_resets.blind_tags and G.GAME.round_resets.blind_tags.Small then
        _blinds.skip_tag['Small'] = G.P_TAGS[G.GAME.round_resets.blind_tags.Small].name
    end

    if G and G.GAME and G.GAME.round_resets and G.GAME.round_resets.blind_tags and G.GAME.round_resets.blind_tags.Big then
        _blinds.skip_tag['Big'] = G.P_TAGS[G.GAME.round_resets.blind_tags.Big].name
    end

    return _blinds
end

function Utils.getAnteData()
    local _ante = { }
    _ante.blinds = Utils.getBlindData()

    return _ante
end

function Utils.getBackData()
    local _back = { }

    return _back
end

function Utils.getShopData()
    local _shop = { }
    if not G or not G.shop then return _shop end
    
    _shop.reroll_cost = G.GAME.current_round.reroll_cost
    _shop.cards = { }
    _shop.boosters = { }
    _shop.vouchers = { }

    for i = 1, #G.shop_jokers.cards do
        _shop.cards[i] = Utils.getCardData(G.shop_jokers.cards[i])
    end

    for i = 1, #G.shop_booster.cards do
        _shop.boosters[i] = Utils.getCardData(G.shop_booster.cards[i])
    end

    for i = 1, #G.shop_vouchers.cards do
        _shop.vouchers[i] = Utils.getCardData(G.shop_vouchers.cards[i])
    end

    return _shop
end

function Utils.getHandScoreData()
    local _handscores = { }

    return _handscores
end

function Utils.getTagsData()
    local _tags = { }

    if G and G.GAME.tags then
        for i = 1, #G.GAME.tags do
            local _tag = Utils.getTag(G.GAME.tags[i])
            _tags[i] = _tag
        end
    end

    return _tags
end

function Utils.getRoundData()
    local _current_round = { }

    if G and G.GAME and G.GAME.current_round then
        _current_round.discards_left = G.GAME.current_round.discards_left
    end

    return _current_round
end

function Utils.getGameData()
    local _game = { }

    if G and G.STATE then
        _game.state = G.STATE
        _game.num_hands_played = G.GAME.hands_played
        _game.num_skips = G.GAME.Skips
        _game.round = G.GAME.round
        _game.discount_percent = G.GAME.discount_percent
        _game.interest_cap = G.GAME.interest_cap
        _game.inflation = G.GAME.inflation
        _game.dollars = G.GAME.dollars
        _game.max_jokers = G.GAME.max_jokers
        _game.bankrupt_at = G.GAME.bankrupt_at
        _game.chips = _game.chips
    end

    return _game
end

function Utils.getTag(tag)
    local _tag = { }

    _tag.name = tag.name

    return _tag
end

function Utils.getGamestate()
    -- TODO
    local _gamestate = { }

    _gamestate = Utils.getGameData()
    
    _gamestate.deckback = Utils.getBackData()
    _gamestate.deck = Utils.getDeckData() -- Ensure this is not ordered
    _gamestate.hand = Utils.getHandData()
    _gamestate.jokers = Utils.getJokersData()
    _gamestate.consumables = Utils.getConsumablesData()
    _gamestate.ante = Utils.getAnteData()
    _gamestate.shop = Utils.getShopData() -- Empty if not in shop phase
    _gamestate.handscores = Utils.getHandScoreData()
    _gamestate.tags = Utils.getTagsData()
    _gamestate.current_round = Utils.getRoundData()
    _gamestate.pack_cards = Utils.getPackCardsData()

    return _gamestate
end

function Utils.parseaction(data)
    -- Protocol is ACTION|arg1|arg2
    action = data:match("^([%a%u_]*)")
    params = data:match("|(.*)")

    if action then
        local _action = Bot.ACTIONS[action]

        if not _action then
            return nil
        end

        local _actiontable = { }
        _actiontable[1] = _action

        if params then
            local _i = 2
            for _arg in params:gmatch("[%w%s,]+") do
                local _splitstring = { }
                local _j = 1
                for _str in _arg:gmatch('([^,]+)') do
                    _splitstring[_j] = tonumber(_str) or _str
                    _j = _j + 1
                end
                _actiontable[_i] = _splitstring
                _i = _i + 1
            end
        end

        return _actiontable
    end
end

Utils.ERROR = {
    NOERROR = 1,
    NUMPARAMS = 2,
    MSGFORMAT = 3,
    INVALIDACTION = 4,
}

function Utils.validateAction(action)
    if action and #action > 1 and #action > Bot.ACTIONPARAMS[action[1]].num_args then
        return Utils.ERROR.NUMPARAMS
    elseif not action then
        return Utils.ERROR.MSGFORMAT
    else
        if not Bot.ACTIONPARAMS[action[1]].isvalid(action) then
            return Utils.ERROR.INVALIDACTION
        end
    end

    return Utils.ERROR.NOERROR
end

function Utils.isTableUnique(table)
    if table == nil then return true end

    local _seen = { }
    for i = 1, #table do
        if _seen[table[i]] then return false end
        _seen[table[i]] = table[i]
    end

    return true
end

function Utils.isTableInRange(table, min, max)
    if table == nil then return true end

    for i = 1, #table do
        if table[i] < min or table[i] > max then return false end
    end
    return true
end

return Utils