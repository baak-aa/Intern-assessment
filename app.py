import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from chatbot import TSLChatbot

# Set page config
st.set_page_config(
    page_title="TSLA Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize the chatbot (cached)
@st.cache_resource
def get_chatbot():
    api_key_status = "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET"
    print(f"DEBUG: GEMINI_API_KEY status inside get_chatbot: {api_key_status}")
    print(f"DEBUG: GEMINI_API_KEY starts with: {str(os.getenv('GEMINI_API_KEY'))[:5]}...")
    return TSLChatbot()

def create_candlestick_chart(df):
    """Create a static candlestick chart with markers and bands"""
    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='TSLA'
    ))

    # Add support bands
    for idx, row in df.iterrows():
        if isinstance(row['Support'], list) and len(row['Support']) > 0:
            support_lower = min(row['Support'])
            support_upper = max(row['Support'])
            fig.add_trace(go.Scatter(
                x=[row['timestamp'], row['timestamp']],
                y=[support_lower, support_upper],
                fill='tonexty',
                mode='lines',
                line_color='green',
                name='Support Band',
                opacity=0.3,
                showlegend=False
            ))

    # Add resistance bands
    for idx, row in df.iterrows():
        if isinstance(row['Resistance'], list) and len(row['Resistance']) > 0:
            resistance_lower = min(row['Resistance'])
            resistance_upper = max(row['Resistance'])
            fig.add_trace(go.Scatter(
                x=[row['timestamp'], row['timestamp']],
                y=[resistance_lower, resistance_upper],
                fill='tonexty',
                mode='lines',
                line_color='red',
                name='Resistance Band',
                opacity=0.3,
                showlegend=False
            ))

    # Add direction markers
    for idx, row in df.iterrows():
        if row['direction'] == 'LONG':
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['low'] * 0.99],
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='green'),
                name='LONG',
                showlegend=False
            ))
        elif row['direction'] == 'SHORT':
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['high'] * 1.01],
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='red'),
                name='SHORT',
                showlegend=False
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['close']],
                mode='markers',
                marker=dict(symbol='circle', size=10, color='yellow'),
                name='None',
                showlegend=False
            ))

    # Update layout
    fig.update_layout(
        title='TSLA Stock Price with Support/Resistance Bands',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        showlegend=True,
        height=800,
        xaxis=dict(rangeslider=dict(visible=True), type="date")
    )

    return fig

def main():
    st.title("📈 TSLA Stock Analysis Dashboard")
    
    tab1, tab2 = st.tabs(["Chart Analysis", "AI Assistant"])
    
    with tab1:
        st.subheader("Interactive Chart")
        try:
            chatbot = get_chatbot()
            df = chatbot.df

            if df is None or df.empty:
                st.error("Error: No stock data available.")
            else:
                fig = create_candlestick_chart(df)
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    with tab2:
        st.subheader("AI Assistant")

        example_questions = [
            "What was the highest price in the dataset?",
            "Show me the trading patterns for the last month",
            "What were the most common support levels?",
            "Analyze the volume trends",
            "What was the average trading volume?",
            "Show me the price trend over the last 30 days"
        ]

        st.subheader("Example Questions")
        cols = st.columns(3)
        for i, question in enumerate(example_questions):
            if cols[i % 3].button(question, key=f"btn_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": question})
                response = chatbot.generate_response(question)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

        st.subheader("Chat with the Bot")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"👤 You: {message['content']}")
            else:
                st.write(f"🤖 Bot: {message['content']}")

        user_query = st.text_input("Ask a question about TSLA stock data:", key="user_input")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.spinner("Analyzing..."):
                response = chatbot.generate_response(user_query)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
