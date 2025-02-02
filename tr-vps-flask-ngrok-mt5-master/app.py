from flask import Flask, jsonify, request
import MetaTrader5 as mt5
from waitress import serve
#from app import app  # Ensure your Flask app instance is imported

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the MetaTrader Flask API"

@app.route('/account_info', methods=['GET'])
def account_info():
    account_info = mt5.account_info()._asdict()
    return jsonify(account_info)

@app.route('/init_mt5', methods=['POST'])
def init_mt5():
    # Daten von der POST-Anfrage empfangen
    data = request.json
    print(f"Empfangene Daten: {data}")

   # Initialize MT5
    if not mt5.initialize():
        print("initialize() failed")
        return jsonify({"error": "MT5 initialization failed"}), 500
    
    # request connection status and parameters
    #print("Terminal Info: ",mt5.terminal_info())
    # get data on MetaTrader 5 version
    print("MT5 Version: ",mt5.version())
    print("Initialize Successfull")
    return jsonify({"message": "MT5 Initialize Successfull"}), 200
    
@app.route('/login_mt5', methods=['POST'])
def login_mt5():
    # Login to MT5 account
    account_number = "***"  # Replace with your account number
    password = "***"  # Replace with your password
    server = "VantageInternational-Demo"  # Replace with your broker server

    if not mt5.login(account_number, password, server):
        return jsonify({"error": "MT5 login failed"}), 401
    
    print("Login Successfull")
    return jsonify({"message": "MT5 login Successfull"}), 200

@app.route('/order', methods=['POST'])
def order():
    # Example order request
    # { "symbol": "EURUSD", "volume": 0.1, "type": "BUY" }
    data = request.json
    symbol = data.get("symbol")
    volume = data.get("volume")
    order_type = data.get("type").upper()

    if order_type == "BUY":
        order_type = mt5.ORDER_BUY
    elif order_type == "SELL":
        order_type = mt5.ORDER_SELL
    else:
        return jsonify({"error": "Invalid order type"}), 400

    # Prepare the request
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_BUY else mt5.symbol_info_tick(symbol).bid,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # Send the order
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return jsonify({"error": result._asdict()}), 500

    return jsonify({"result": result._asdict()})

app.route('/execute_trade', methods=['POST'])
def execute_trade():
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    lot = data.get('lot', 0.1)

    # Initialize MT5
    if not mt5.initialize():
        print("initialize() failed")
        return jsonify({"error": "MT5 initialization failed"}), 500

    # Login to MT5 account
    account_number = "***" # Replace with your account number
    password = "your_password"  # Replace with your password
    server = "your_broker_server"  # Replace with your broker server

    if not mt5.login(account_number, password, server):
        return jsonify({"error": "MT5 login failed"}), 401

    # Select the symbol
    if not mt5.symbol_select(symbol, True):
        return jsonify({"error": f"Failed to select symbol {symbol}"}), 400

    # Get the current price
    price = mt5.symbol_info_tick(symbol).ask
    stop_loss = price - 100 * mt5.symbol_info(symbol).point
    take_profit = price + 100 * mt5.symbol_info(symbol).point

    # Prepare the order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 234000,
        "comment": "API order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # Send the order
    result = mt5.order_send(request)

    # Shutdown MT5
    mt5.shutdown()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return jsonify({"error": f"Order failed, retcode = {result.retcode}"}), 500

    return jsonify({"message": "Order placed successfully", "order": result._asdict()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    #app.run(host='127.0.0.1', port=5000)
    #serve(app, host='0.0.0.0', port=5000)
    #serve(app, host='127.0.0.1', port=5000)
