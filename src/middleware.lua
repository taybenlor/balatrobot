
Middleware = { }
Middleware.choosingboostercards = false

Middleware.queuedactions = List.new()
Middleware.currentaction = nil
Middleware.conditionalactions = { }

Middleware.BUTTONS = {

    -- Shop Phase Buttons
    NEXT_ROUND = nil,
    REROLL = nil,

    -- Pack Phase Buttons
    SKIP_PACK = nil,

}

function random_key(tb)
    local keys = {}
    for k in pairs(tb) do table.insert(keys, k) end
    return keys[math.random(#keys)]
end

function random_element(tb)
    local keys = {}
    for k in pairs(tb) do table.insert(keys, k) end
    return tb[keys[math.random(#keys)]]
end

function Middleware.add_event_sequence(events)

    local _lastevent = nil
    local _totaldelay = 0.0

    for k, event in pairs(events) do
        _totaldelay = _totaldelay + event.delay

        local _event = Event({
            trigger = 'after',
            delay = _totaldelay,
            blocking = false,
            func = function()
                event.func(event.args)
                return true
            end
        })
        G.E_MANAGER:add_event(_event)
        _lastevent = _event
    end

    return _lastevent
end

local function firewhenready(condition, func)
    for i = 1, #Middleware.conditionalactions do
        if Middleware.conditionalactions[i] == nil then
            Middleware.conditionalactions[i] = {
                ready = condition,
                fire = func
            }
            return nil
        end
    end

    Middleware.conditionalactions[#Middleware.conditionalactions + 1] = {
        ready = condition,
        fire = func
    }
end

local function queueaction(func, delay)

    if not delay then
        delay = Bot.SETTINGS.action_delay
    end

    List.pushleft(Middleware.queuedactions, { func = func, delay = delay })
end

local function pushbutton(button, delay)
    queueaction(function()
        if button and button.config and button.config.button then
            G.FUNCS[button.config.button](button)
        end
    end, delay)
end

local function pushbutton_instant(button, delay)
    if button and button.config and button.config.button then
        G.FUNCS[button.config.button](button)
    end
end

local function clickcard(card, delay)
    queueaction(function()
        --if card and card.click then
            card:click()
        --end
    end, delay)
end

local function sellcard(card, delay)
    queueaction(function()
        local _use_button = nil
        local _use_button = card.children.use_button and card.children.use_button.definition
        if _use_button and _use_button.config.button == nil then
            local _node_index = card.ability.consumeable and 2 or 1
            _use_button = _use_button.nodes[_node_index]

            if card.area and card.area.config.type == 'joker' then
                local _use_button = card.children.use_button.definition.nodes[1].nodes[1].nodes[1].nodes[1]
                pushbutton_instant(_use_button, delay)
            else
                pushbutton_instant(_use_button, delay)
            end

            return
        end
    end, delay)
end

local function usecard(card, delay)

    queueaction(function()
        
        -- if _use_button and _use_button.config.button == nil then
        --     local _node_index = card.ability.consumeable and 2 or 1
        --     _use_button = _use_button.nodes[_node_index]

        --     if card.area and card.area.config.type == 'joker' then
        --         sendDebugMessage("WE ARE HERE!")
        --         local _use_button = card.children.use_button
        --         sendDebugMessage("WEVE GOT A USE BUTTON")
        --         -- local _use_button = card.children.use_button.definition.nodes[1].nodes[1].nodes[1].nodes[1]
        --         pushbutton_instant(_use_button, delay)
        --     else
        --         pushbutton_instant(_use_button, delay)
        --     end

        --     return
        -- end
        local _buy_and_use_button = card.children.buy_and_use_button and card.children.buy_and_use_button.definition
        local _buy_button = card.children.buy_button and card.children.buy_button.definition
        local _use_button = card.children.use_button and card.children.use_button.definition
        
        if _buy_and_use_button then
            pushbutton_instant(_buy_and_use_button, delay)
        elseif _buy_button then
            pushbutton_instant(_buy_button, delay)
        elseif _use_button then
            -- why use a function when this will work directly? 
            G.FUNCS.use_card({config = {ref_table = card}})
        end
    end, delay)
end

local function c_update()

    -- Process the queue of Bot events, max 1 per frame
    _events = { }
    if not List.isempty(Middleware.queuedactions) and
        (not Middleware.currentaction or 
            (Middleware.currentaction and Middleware.currentaction.complete)) then

        local _func_and_delay = List.popright(Middleware.queuedactions)
        Middleware.currentaction = Middleware.add_event_sequence({{ func = _func_and_delay.func, delay = _func_and_delay.delay }})
    end

    -- Run functions that have been waiting for a condition to be met
    for i = 1, #Middleware.conditionalactions do
        if Middleware.conditionalactions[i] then
            local _result = {Middleware.conditionalactions[i].ready()}
            local _ready = table.remove(_result, 1)
            if _ready == true then
                Middleware.conditionalactions[i].fire(unpack(_result))
                Middleware.conditionalactions[i] = nil
            end
        end
    end
end

function Middleware.c_play_hand()

    firewhenready(function()
        local _action, _cards_to_play = Bot.select_cards_from_hand()
        if _action and _cards_to_play then
            return true, _action, _cards_to_play
        else
            return false
        end
    end, 
    
    function(_action, _cards_to_play)
        -- Option 1: Play Hand
        if _action == Bot.ACTIONS.PLAY_HAND then
            for i = 1, #_cards_to_play do
                clickcard(G.hand.cards[_cards_to_play[i]])
            end
            local _play_button = UIBox:get_UIE_by_ID('play_button', G.buttons.UIRoot)
            pushbutton(_play_button)
        end
    
        -- Option 2: Discard Hand
        if _action == Bot.ACTIONS.DISCARD_HAND then
            for i = 1, #_cards_to_play do
                clickcard(G.hand.cards[_cards_to_play[i]])
            end
            local _discard_button = UIBox:get_UIE_by_ID('discard_button', G.buttons.UIRoot)
            pushbutton(_discard_button)
        end

        if _action == Bot.ACTIONS.REARRANGE_HAND then
            for k,v in ipairs(_cards_to_play) do
                if k < v then
                    G.hand.cards[k], G.hand.cards[v] = G.hand.cards[v], G.hand.cards[k]
                end
            end

            G.hand:set_ranks()
        end

        if _action == Bot.ACTIONS.REARRANGE_JOKERS then
            for k,v in ipairs(_cards_to_play) do
                if k < v then
                    G.jokers.cards[k], G.jokers.cards[v] = G.jokers.cards[v], G.jokers.cards[k]
                end
            end

            G.jokers:set_ranks()
        end
    end)
end

function Middleware.c_select_blind()
    firewhenready(function()
        local _blind_on_deck = G.GAME.blind_on_deck
        if G.GAME.blind_on_deck == 'Small' or G.GAME.blind_on_deck == 'Big' or G.GAME.blind_on_deck == 'Boss' then
            local _action = Bot.skip_or_select_blind(_blind_on_deck)

            if _action then
                return true, _action
            else
                return false
            end
        end
        return false
    end,

    function(_action)
        local _blind_on_deck = G.GAME.blind_on_deck
        local _blind_obj = G.blind_select_opts[string.lower(_blind_on_deck)]

        local _button = nil
        if _action == Bot.ACTIONS.SELECT_BLIND then
            local _select_button = _blind_obj:get_UIE_by_ID('select_blind_button')
            _button = _select_button
        elseif _action == Bot.ACTIONS.SKIP_BLIND and _blind_on_deck ~= 'Boss' then
            local _skip_button = _blind_obj:get_UIE_by_ID('tag_'.._blind_on_deck).children[2]
            _button = _skip_button
        else
            -- Default to selecting the blind if action is not recognized
            _button = _blind_obj:get_UIE_by_ID('select_blind_button') 
        end
    
        pushbutton(_button)
    end)
end


function Middleware.c_choose_booster_cards()
    sendDebugMessage("Start of outer booster card function!")
    if Middleware.choosingboostercards == true then return end
    if not G.pack_cards.cards then return end

    Middleware.choosingboostercards = true
    
    sendDebugMessage("Passed checks!")

    firewhenready(function()
        local _action, _card, _hand_cards = Bot.select_booster_action(G.pack_cards.cards, G.hand.cards)
        if _action then
            return true, _action, _card, _hand_cards
        else
            return false
        end
    end,

    function(_action, _card, _hand_cards)
        sendDebugMessage("Start of inner booster card function!")
        if _action == Bot.ACTIONS.SKIP_BOOSTER_PACK then
            pushbutton(Middleware.BUTTONS.SKIP_PACK)
            if G.GAME.PACK_INTERRUPT == G.STATES.BLIND_SELECT then
                sendDebugMessage("Queueing blind select action!")
                queueaction(function()
                        firewhenready(function()
                            return G.STATE_COMPLETE and G.STATE == G.STATES.BLIND_SELECT
                        end, function()
                            Middleware.choosingboostercards = false
                            Middleware.c_select_blind()
                        end)
                    end, 0.0)
            elseif G.GAME.PACK_INTERRUPT == G.STATES.SHOP then
                queueaction(function()
                    sendDebugMessage("Queueing shop action!")
                    firewhenready(function()
                        return G.STATE_COMPLETE and G.STATE == G.STATES.SHOP
                    end, function()
                        Middleware.choosingboostercards = false
                        Middleware.c_shop()
                    end)
                end, 0.0)
            end
        elseif _action == Bot.ACTIONS.SELECT_BOOSTER_CARD then
            -- Defensive: Ensure _card and _card[1] are valid
            local card_index = _card and _card[1]
            local selected_card = nil
            if card_index and G.pack_cards and G.pack_cards.cards then
                selected_card = card_index and G.pack_cards.cards[card_index]
            end
            local max_highlighted = 0
            if selected_card and selected_card.ability and selected_card.ability.max_highlighted then
                max_highlighted = selected_card.ability.max_highlighted
            end

            -- Defensive: Ensure _hand_cards is a table
            if type(_hand_cards) ~= "table" then
                _hand_cards = {}
            end

            -- Pad or trim _hand_cards to match max_highlighted
            if max_highlighted > 0 then
                while #_hand_cards < max_highlighted do
                    table.insert(_hand_cards, #_hand_cards + 1)
                end
                while #_hand_cards > max_highlighted do
                    table.remove(_hand_cards)
                end
            end

            -- Click each card from your deck first (only occurs if _pack_card is consumable)
            if (_hand_cards ~= nil) then
                for i = 1, #_hand_cards do
                    if G.hand.cards and G.hand.cards[_hand_cards[i]] then
                        clickcard(G.hand.cards[_hand_cards[i]])
                    end
                end
            end

            -- actually make the change
            if selected_card then
                clickcard(selected_card)
                usecard(selected_card)
            end

            Middleware.choosingboostercards = false

            -- if we have more choices to make, re-queue the action
            if G.GAME.pack_choices and G.GAME.pack_choices - 1 > 1 then
                sendDebugMessage("Re-queueing choose booster card action!")
                queueaction(function()
                    Middleware.choosingboostercards = false
                    Middleware.c_choose_booster_cards()
                end, 0.0)
                return
            elseif G.GAME.PACK_INTERRUPT == G.STATES.BLIND_SELECT then
                sendDebugMessage("Queueing blind select action!")
                queueaction(function()
                        firewhenready(function()
                            return G.STATE_COMPLETE and G.STATE == G.STATES.BLIND_SELECT
                        end, function()
                            Middleware.choosingboostercards = false
                            Middleware.c_select_blind()
                        end)
                    end, 0.0)
            elseif G.GAME.PACK_INTERRUPT == G.STATES.SHOP then
                queueaction(function()
                    sendDebugMessage("Queueing shop action!")
                    firewhenready(function()
                        return G.STATE_COMPLETE and G.STATE == G.STATES.SHOP
                    end, function()
                        Middleware.choosingboostercards = false
                        Middleware.c_shop()
                    end)
                end, 0.0)
            end
        end
    end)
end


function Middleware.c_shop()

    local _done_shopping = false

    local _b_round_end_shop = true
    local _b_reroll_shop = Middleware.BUTTONS.REROLL and Middleware.BUTTONS.REROLL.config and Middleware.BUTTONS.REROLL.config.button

    local _cards_to_buy = { }
    if G.shop_jokers.cards and #G.shop_jokers.cards > 0 then
        for i = 1, #G.shop_jokers.cards do
            _cards_to_buy[i] = G.shop_jokers.cards[i].cost <= G.GAME.dollars and G.shop_jokers.cards[i] or nil
        end
    end

    local _vouchers_to_buy = { }
    if G.shop_vouchers.cards and #G.shop_vouchers.cards > 0 then
        for i = 1, #G.shop_vouchers.cards do
            _vouchers_to_buy[i] = G.shop_vouchers.cards[i].cost <= G.GAME.dollars and G.shop_vouchers.cards[i] or nil
        end
    end

    local _boosters_to_buy = { }
    if G.shop_booster.cards and #G.shop_booster.cards > 0 then
        for i = 1, #G.shop_booster.cards do
            _boosters_to_buy[i] = G.shop_booster.cards[i].cost <= G.GAME.dollars and G.shop_booster.cards[i] or nil
        end
    end

    local _choices = { }
    _choices[Bot.ACTIONS.END_SHOP] = _b_round_end_shop
    _choices[Bot.ACTIONS.REROLL_SHOP] = _b_reroll_shop
    _choices[Bot.ACTIONS.BUY_CARD] = #_cards_to_buy > 0 and _cards_to_buy or nil
    _choices[Bot.ACTIONS.BUY_VOUCHER] = #_vouchers_to_buy > 0 and _vouchers_to_buy or nil
    _choices[Bot.ACTIONS.BUY_BOOSTER] = #_boosters_to_buy > 0 and _boosters_to_buy or nil
    
    firewhenready(function()
        local _action, _card = Bot.select_shop_action(_choices)
        if _action then
            return true, _action, _card
        else
            return false
        end
    end,

    function(_action, _card)
        sendDebugMessage("hello!")
        if _action == Bot.ACTIONS.END_SHOP then
            pushbutton(Middleware.BUTTONS.NEXT_ROUND)
            _done_shopping = true
        elseif _action == Bot.ACTIONS.REROLL_SHOP then
            pushbutton(Middleware.BUTTONS.REROLL)
        elseif _action == Bot.ACTIONS.BUY_CARD then
            clickcard(G.shop_jokers.cards[_card[1]])
            usecard(G.shop_jokers.cards[_card[1]])
        elseif _action == Bot.ACTIONS.BUY_VOUCHER then
            clickcard(G.shop_vouchers.cards[_card[1]])
            usecard(G.shop_vouchers.cards[_card[1]])
        elseif _action == Bot.ACTIONS.BUY_BOOSTER then
            _done_shopping = true
            clickcard(G.shop_booster.cards[_card[1]])
            usecard(G.shop_booster.cards[_card[1]])
        elseif _action == Bot.ACTIONS.SELL_JOKER then
            clickcard(G.jokers.cards[_card[1]])
            sellcard(G.jokers.cards[_card[1]])
        end
        
        sendDebugMessage("hello again!")

        if not _done_shopping then
            queueaction(function()
                firewhenready(function()
                    return G.shop ~= nil and G.STATE_COMPLETE and G.STATE == G.STATES.SHOP
                end, Middleware.c_shop)
            end)
        end
    end)
    
end

-- function Middleware.c_rearrange_hand()

--     firewhenready(function()
--         local _action, _order = Bot.rearrange_hand()
--         if _action then
--             return true, _action, _order
--         else
--             return false
--         end
--     end,

--     function(_action, _order)
--         Middleware.c_play_hand()

--         if not _order or #_order ~= #G.hand.cards then return end

--         queueaction(function()
--             for k,v in ipairs(_order) do
--                 if k < v then
--                     G.hand.cards[k], G.hand.cards[v] = G.hand.cards[v], G.hand.cards[k]
--                 end
--             end

--             G.hand:set_ranks()
--         end)
--     end)

-- end

-- function Middleware.c_rearrange_consumables()

--     firewhenready(function()
--         local _action, _order = Bot.rearrange_consumables()
--         if _action then
--             return true, _action, _order
--         else
--             return false
--         end
--     end,

--     function(_action, _order)
--         -- Middleware.c_rearrange_hand()

--         if not G.consumeables then return end
--         if not G.consumeables.cards then return end
--         if not _order or #_order ~= #G.consumeables.cards  then return end

--         queueaction(function()
--             for k,v in ipairs(_order) do
--                 if k < v then
--                     G.consumeables.cards[k], G.consumeables.cards[v] = G.consumeables.cards[v], G.consumeables.cards[k]
--                 end
--             end

--             G.consumeables:set_ranks()
--         end)
--     end)

-- end

function Middleware.c_use_or_sell_consumables()
    
    sendDebugMessage("We are in the outer sell consumables function!")

    firewhenready(function()
        local _action, _cards, _hand_cards = Bot.use_or_sell_consumables()
        if _action then
            return true, _action, _cards, _hand_cards
        else
            return false
        end
    end,

    function(_action, _cards, _hand_cards)
        sendDebugMessage("We are in the inner sell consumables function!")
        if _action == Bot.ACTIONS.SELL_CONSUMABLE and _cards then
            for i = 1, #_cards do
                if G.consumeables.cards and G.consumeables.cards[_cards[i]] then
                    clickcard(G.consumeables.cards[_cards[i]])
                    sellcard(G.consumeables.cards[_cards[i]], 1)
                end
            end
        elseif _action == Bot.ACTIONS.USE_CONSUMABLE and _cards then
            sendDebugMessage("We are using a consumable!")
            if (_hand_cards ~= nil) then
                for i = 1, #_hand_cards do
                    sendDebugMessage("Clicking cards in hand!")
                    if G.hand.cards and G.hand.cards[_hand_cards[i]] then
                        sendDebugMessage("Clicking card in hand!")
                        clickcard(G.hand.cards[_hand_cards[i]])
                    end
                end
            end
            if G.consumeables.cards and G.consumeables.cards[_cards[1]] then
                sendDebugMessage("Clicking consumable card!")
                clickcard(G.consumeables.cards[_cards[1]])
                usecard(G.consumeables.cards[_cards[1]], 2)
            end
        end
        -- Jump straight to play hand
        Middleware.c_play_hand()
        -- Middleware.c_rearrange_consumables()
    end)

end


-- function Middleware.c_rearrange_jokers()
    
--     firewhenready(function()
--         local _action, _order = Bot.rearrange_jokers()
--         if _action then
--             return true, _action, _order
--         else
--             return false
--         end
--     end,

--     function(_action, _order)
--         Middleware.c_use_or_sell_consumables()

--         if not _order or #_order ~= #G.jokers.cards then return end

--         queueaction(function()
--             for k,v in ipairs(_order) do
--                 if k < v then
--                     G.jokers.cards[k], G.jokers.cards[v] = G.jokers.cards[v], G.jokers.cards[k]
--                 end
--             end

--             G.jokers:set_ranks()
--         end)
--     end)

-- end

-- function Middleware.c_sell_jokers()

--     sendDebugMessage("Start of outer sell joker function!")
--     if not G.jokers.cards then return end

--     firewhenready(function()
--         local _action, _cards = Bot.sell_jokers()
--         if _action and _cards ~= nil then
--             sendDebugMessage('action and cards')
--             sendDebugMessage(_action)
--             sendDebugMessage(_cards)
--             return true, _action, _cards
--         elseif _action then
--             sendDebugMessage('action')
--             sendDebugMessage(_action)
--             return true, _action, nil
--         else
--             sendDebugMessage('no action or cards')
--             return false
--         end
--     end,

--     function(_action, _cards)
--         sendDebugMessage("Reached the inner function for sell jokers!")
--         if _action == Bot.ACTIONS.SELL_JOKER and _cards then
--             for i = 1, #_cards do
--                 sendDebugMessage("trying to click a joker!")
--                 clickcard(G.jokers.cards[_cards[i]])
--                 usecard(G.jokers.cards[_cards[i]])
--             end
--         end
--         Middleware.c_rearrange_jokers()
--     end)
-- end

function Middleware.c_start_run()

    firewhenready(function()
        local _action, _stake, _deck, _seed, _challenge = Bot.start_run()
        _stake = _stake ~= nil and tonumber(_stake[1]) or 1
        _deck = _deck ~= nil and _deck[1] or "Red Deck"
        _seed = _seed ~= nil and _seed[1] or nil
        _challenge = _challenge ~= nil and _challenge[1] or nil
        if _action then
            return true, _action, _stake, _deck, _seed, _challenge
        else
            return false
        end
    end,

    function(_action, _stake, _deck, _seed, _challenge)
        queueaction(function()
            local _play_button = G.MAIN_MENU_UI:get_UIE_by_ID('main_menu_play')
            G.FUNCS[_play_button.config.button]({
                config = { }
            })
            G.FUNCS.exit_overlay_menu()
        end)

        queueaction(function()
            for k, v in pairs(G.P_CENTER_POOLS.Back) do
                if v.name == _deck then
                    G.GAME.selected_back:change_to(v)
                    G.GAME.viewed_back:change_to(v)
                end
            end

            for i = 1, #G.CHALLENGES do
                if G.CHALLENGES[i].name == _challenge then
                    _challenge = G.CHALLENGES[i]
                end                    
            end
            G.FUNCS.start_run(nil, {stake = _stake, seed = _seed, challenge = _challenge})
        end, 1.0)
    end)
end


local function w_gamestate(...)
    local _t, _k, _v = ...

    -- If we lose a run, we want to go back to the main menu
    -- Before we try to start a new run
    if _k == 'STATE' and _v == G.STATES.GAME_OVER then
        G.FUNCS.go_to_menu({})
    end

    if _k == 'STATE' and _v == G.STATES.MENU then
        Middleware.c_start_run()
    end
end

local function c_initgamehooks()

    -- Hooks break SAVE_MANAGER.channel:push so disable saving. Who needs it when you are botting anyway...
    G.SAVE_MANAGER = {
        channel = {
            push = function() end
        }
    }

    -- Detect when hand has been drawn
    G.GAME.blind.drawn_to_hand = Hook.addcallback(G.GAME.blind.drawn_to_hand, function(...)
        firewhenready(function()
            return G.buttons and G.STATE_COMPLETE and G.STATE == G.STATES.SELECTING_HAND
        end, function()
            Middleware.c_play_hand()
        end)
    end)

    -- Hook button snaps
    G.CONTROLLER.snap_to = Hook.addcallback(G.CONTROLLER.snap_to, function(...)
        local _self = ...

        if _self and _self.snap_cursor_to.node and _self.snap_cursor_to.node.config and _self.snap_cursor_to.node.config.button then
            
            local _button = _self.snap_cursor_to.node
            local _buttonfunc = _self.snap_cursor_to.node.config.button

            if _buttonfunc == 'select_blind' and G.STATE == G.STATES.BLIND_SELECT then
                Middleware.c_select_blind()
            elseif _buttonfunc == 'cash_out' then
                pushbutton(_button)
            elseif _buttonfunc == 'toggle_shop' and G.shop ~= nil then -- 'next_round_button'
                Middleware.BUTTONS.NEXT_ROUND = _button

                firewhenready(function()
                    return G.shop ~= nil and G.STATE_COMPLETE and G.STATE == G.STATES.SHOP
                end, Middleware.c_shop)
            end
        end
    end)

    -- Set reroll availability
    G.FUNCS.can_reroll = Hook.addcallback(G.FUNCS.can_reroll, function(...)
        local _e = ...
        Middleware.BUTTONS.REROLL = _e
    end)

    -- Booster pack skip availability
    G.FUNCS.can_skip_booster = Hook.addcallback(G.FUNCS.can_skip_booster, function(...)
        local _e = ...
        Middleware.BUTTONS.SKIP_PACK = _e
        if Middleware.BUTTONS.SKIP_PACK ~= nil and
        Middleware.BUTTONS.SKIP_PACK.config.button == 'skip_booster' and
        Middleware.choosingboostercards == false and
        G and G.pack_cards and G.pack_cards.cards then
            Middleware.c_choose_booster_cards()
        end
    end)
end

function Middleware.hookbalatro()
    -- Unlock all card backs
    for k, v in pairs(G.P_CENTERS) do
        if not v.demo and not v.wip and v.set == "Back" then 
            v.alerted = true
            v.discovered = true
            v.unlocked = true
        end
    end

    -- Start game from main menu
    G.start_run = Hook.addcallback(G.start_run, c_initgamehooks)
    G = Hook.addonwrite(G, w_gamestate)
    G.update = Hook.addcallback(G.update, c_update)
end

return Middleware