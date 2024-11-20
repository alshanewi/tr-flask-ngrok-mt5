import MetaTrader5 as mt5
import pandas as pd


# function to send a market order
def send_market_order(magic, comment, barclose,symbol, volume, order_type):

    tick = mt5.symbol_info_tick(symbol)
    print("tick MT5 Price: ", tick)
    print("barclose TR Price: ", barclose)
    print("order_type: ", order_type)
    print("magic: ", magic)
    print("comment: ", comment)
    #order_dict = {'buy': mt5.ORDER_TYPE_BUY, 'sell': mt5.ORDER_TYPE_SELL}
    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    sl=0.0
    tp=0.0
    point = mt5.symbol_info(symbol).point
    print("Symbol: ", symbol)
    print("Volume: ", volume)
    print("point: ", point)
    if (order_type=="buy"):
        price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_BUY
        sl = price - 100000 * point
        tp = price + 50000 * point
    elif(order_type=="sell"):
        price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_SELL
        sl = price + 100000 * point
        tp = price - 50000 * point
    deviation = 20
    
    print("price: ", price)
    print("type: ", type)
    print("sl: ", sl)
    print("tp: ", tp)
    
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order_result = mt5.order_send(req)
    print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,volume,price,deviation))

    return order_result

def close_all_positions(alert,order_action, type_filling=mt5.ORDER_FILLING_IOC):
    order_action_dict = {
        'buy': 0,
        'sell': 1
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get() 

        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        if order_action != 'all':
            positions_df = positions_df[(positions_df['type'] == order_action_dict[order_action])]

        for i, position in positions_df.iterrows():
            order_result = close_position(order_action, position, type_filling=type_filling)

            print('order_result: ', order_result)
            print("alert: ", alert)
            print("4. position #{} closed, {}".format(position['ticket'],order_result))

        return order_result

def close_position(order_action, position, deviation=20, magic=1, comment='', type_filling=mt5.ORDER_FILLING_IOC):
    order_type_dict = {
        0: mt5.ORDER_TYPE_SELL,
        1: mt5.ORDER_TYPE_BUY
    }

    price_dict = {
        0: mt5.symbol_info_tick(position['symbol']).bid,
        1: mt5.symbol_info_tick(position['symbol']).ask
    }
    tick = mt5.symbol_info_tick(position['symbol'])
    print("tick MT5 Price: ", tick)
    print("Type: ", order_type_dict[position['type']], " Price: ", price_dict[position['type']])
    print("Type: #{} ,with price {}".format(order_type_dict[position['type']],price_dict[position['type']]))

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position['ticket'],  # select the position you want to close
        "symbol": position['symbol'],
        "volume": position['volume'],  # FLOAT
        "type": order_type_dict[position['type']],
        "price": price_dict[position['type']],
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": order_action,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    print("Request: ", request)

    order_result = mt5.order_send(request)
     # check the execution result
    print("-------Closing trade--------")
    print("3. closing position... #{}: {} {} lots at {} with deviation={} points".format(position['ticket'],position['symbol'],position['volume'],price_dict[position['type']],deviation));
    print("-------Closing trade--------")
    
    return (order_result)


def get_positions():
    if mt5.positions_total():
        positions = mt5.positions_get()
        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        return positions_df

    else:
        return pd.DataFrame()
