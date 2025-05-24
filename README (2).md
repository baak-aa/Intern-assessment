# TSLA Stock Analysis Dashboard

This Streamlit application provides an interactive dashboard for analyzing TSLA stock data, featuring:
- Interactive candlestick chart with TradingView lightweight charts
- Support and resistance bands
- Direction markers (arrows)
- Gemini-powered chatbot for data analysis

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Features

- Interactive candlestick chart with OHLCV data
- Support and resistance bands visualization
- Direction markers (green up arrows for LONG, red down arrows for SHORT)
- AI-powered chatbot for data analysis using Gemini
- Animated chart replay (bonus feature)

## Data Source

The application uses TSLA stock data from the provided spreadsheet, including:
- OHLCV data
- Support and resistance levels
- Trading direction indicators 