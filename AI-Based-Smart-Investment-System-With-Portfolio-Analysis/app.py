from flask import Flask, jsonify, render_template, request
import yfinance as yf

app = Flask(__name__)

# API to fetch stock data
@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    company_symbol = request.args.get('company_symbol')
    try:
        ticker = yf.Ticker(company_symbol)
        company_name = ticker.info.get('longName', 'N/A')
        current_price = ticker.history(period="1d")['Close'].iloc[0]
        historical_data = ticker.history(period="1mo")
        previous_close = historical_data['Close'].iloc[-2] if len(historical_data) > 1 else current_price
        rate_of_return = ((current_price - previous_close) / previous_close) * 100

        history_data = [
            {"date": date.strftime('%Y-%m-%d'), "close": row['Close']}
            for date, row in historical_data.iterrows()
        ]

        return jsonify({
            "company_name": company_name,
            "current_price": current_price,
            "rate_of_return": rate_of_return,
            "history_data": history_data
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# API to fetch mutual fund data
@app.route('/api/mutual-fund-data', methods=['GET'])
def get_mutual_fund_data():
    fund_symbol = request.args.get('fund_symbol')
    try:
        ticker = yf.Ticker(fund_symbol)
        fund_name = ticker.info.get("longName", "N/A")
        current_nav = ticker.info.get("previousClose", 0.0)
        expense_ratio = ticker.info.get("expenseRatio", 0.0) * 100
        historical_data = ticker.history(period="1mo")
        previous_nav = historical_data["Close"].iloc[0] if len(historical_data) > 0 else current_nav
        rate_of_return = ((current_nav - previous_nav) / previous_nav) * 100 if previous_nav else 0.0

        history_data = [
            {"date": date.strftime("%Y-%m-%d"), "nav": row["Close"]}
            for date, row in historical_data.iterrows()
        ]

        return jsonify({
            "fund_name": fund_name,
            "current_nav": current_nav,
            "rate_of_return": rate_of_return,
            "expense_ratio": expense_ratio,
            "history_data": history_data
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# Serve HTML pages
@app.route('/')
def index():
    return render_template('index1.html')

if __name__ == '__main__':
    app.run(debug=True)
