import pandas as pd
from flask import Flask, render_template, request, jsonify
import joblib
import plotly.graph_objs as go
import plotly.io as pio
from sklearn.metrics import r2_score

# Flask app initialization
app = Flask(__name__)

# File path for the trained model
model_path = 'random_forest_model.pkl'

# File paths for stock data
file_paths = {
    "high_cap": "C:/Users/shubh/OneDrive/Desktop/Smart Investment Plan/SIP model/Dataset/high_cap_stock_data_inr_2010_2024.csv",
    "mid_cap": "C:/Users/shubh/OneDrive/Desktop/Smart Investment Plan/SIP model/Dataset/mid_cap_stock_data_inr_2010_2024.csv",
    "low_cap": "C:/Users/shubh/OneDrive/Desktop/Smart Investment Plan/SIP model/Dataset/low_cap_stock_data_inr_2010_2024.csv"
}

# Load and preprocess stock data
def load_and_preprocess(file_path):
    """Loads and preprocesses the stock data."""
    try:
        data = pd.read_csv(file_path)
        data = data.dropna()  # Drop missing values
        data['Date'] = pd.to_datetime(data['Date'])
        data['Year'] = data['Date'].dt.year
        data['Month'] = data['Date'].dt.month
        return data
    except FileNotFoundError as e:
        print(f"Error loading file {file_path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if file is not found

# Combine datasets
datasets = [load_and_preprocess(path) for path in file_paths.values() if not load_and_preprocess(path).empty]

if not datasets:
    print("No data loaded. Exiting...")
    exit()

# Check column consistency and concatenate datasets
assert all(datasets[0].columns.equals(data.columns) for data in datasets), "Inconsistent columns in datasets."
combined_data = pd.concat(datasets, ignore_index=True)

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles prediction requests and integrates accuracy graph."""
    try:
        # Load the trained model
        rf_model = joblib.load(model_path)
    except Exception as e:
        return jsonify({"error": f"Model loading failed: {str(e)}"})

    # Parse input from form
    try:
        investment_term = request.form['investment_term']
        target_amount = float(request.form['target_amount'])
        max_loss = float(request.form['max_loss']) / 100  # Convert percentage to decimal
    except ValueError:
        return render_template('index1.html', message="Invalid input, please enter valid numbers.")

    # Filter data based on investment term
    filtered_data = combined_data
    current_year = pd.Timestamp.now().year

    if investment_term == "Short":
        filtered_data = filtered_data[filtered_data['Year'] >= (current_year - 2)]
    elif investment_term == "Medium":
        filtered_data = filtered_data[(filtered_data['Year'] >= (current_year - 6)) & (filtered_data['Year'] < (current_year - 2))]
    else:  # Long-term investment
        filtered_data = filtered_data[filtered_data['Year'] < (current_year - 6)]

    if filtered_data.empty:
        return render_template('index.html', message="No data available for the selected filters.")

    # Prepare data for prediction
    X_filtered = filtered_data[['Open', 'High', 'Low', 'Close', 'Volume', 'Year', 'Month']]
    y_actual = filtered_data['Close']  # Actual close prices

    try:
        filtered_data['Predicted_Close'] = rf_model.predict(X_filtered)
    except Exception as e:
        return render_template('index.html', message=f"Prediction failed: {str(e)}")

    # Evaluate model accuracy (R² score)
    r2 = r2_score(y_actual, filtered_data['Predicted_Close'])

    # Generate accuracy graph (Actual vs Predicted)
    accuracy_fig = go.Figure()
    accuracy_fig.add_trace(go.Scatter(
        x=y_actual,
        y=filtered_data['Predicted_Close'],
        mode='markers',
        name='Predicted vs Actual'
    ))
    accuracy_fig.update_layout(
        title=f"Model Accuracy (R² Score: {r2:.2f})",
        xaxis_title="Actual Close Price",
        yaxis_title="Predicted Close Price",
        template="plotly_white"
    )
    accuracy_graph_html = pio.to_html(accuracy_fig, full_html=False)

    # Filter recommendations
    recommended_stocks = filtered_data[
        (filtered_data['Predicted_Close'] <= target_amount) & 
        (filtered_data['Predicted_Close'] >= target_amount * (1 - max_loss))
    ].sort_values(by='Predicted_Close', ascending=False)

    if not recommended_stocks.empty:
        # Extract unique company names and predicted close prices
        unique_companies = recommended_stocks[['Company', 'Predicted_Close']].drop_duplicates(subset='Company').head(10)
        company_names = unique_companies['Company'].tolist()

        # Generate stock prediction graph
        stock_fig = go.Figure()
        stock_fig.add_trace(go.Scatter(
            x=recommended_stocks['Date'],
            y=recommended_stocks['Predicted_Close'],
            mode='lines+markers',
            name='Predicted Close'
        ))
        stock_fig.update_layout(
            title="Stock Price Prediction for Matching Stocks",
            xaxis_title="Date",
            yaxis_title="Predicted Close Price",
            template="plotly_white"
        )
        stock_graph_html = pio.to_html(stock_fig, full_html=False)

        return render_template('index.html',
                               company_names=company_names,
                               graph=stock_graph_html,
                               accuracy_graph=accuracy_graph_html,
                               investment_term=investment_term,
                               target_amount=target_amount,
                               max_loss=max_loss,
                               message="Matching Stocks Found!")
    else:
        return render_template('index.html',
                               accuracy_graph=accuracy_graph_html,
                               investment_term=investment_term,
                               target_amount=target_amount,
                               max_loss=max_loss,
                               message="No Matching Stocks Found. Please Adjust Your Preferences.")

if __name__ == '__main__':
    app.run(debug=True)
