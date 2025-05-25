import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv
from data_processor import load_tsla_data, calculate_direction_markers, get_animation_frames
from chatbot import TSLChatbot
import time

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
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False
if 'stop_animation' not in st.session_state:
    st.session_state.stop_animation = False

# Initialize the chatbot (cache once)
@st.cache_resource
def get_chatbot():
    return TSLChatbot()

def create_candlestick_chart(df):
    fig = go.Figure()

    # Add candlestick trace
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
                showlegend=False
            ))
        elif row['direction'] == 'SHORT':
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['high'] * 1.01],
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='red'),
                showlegend=False
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['close']],
                mode='markers',
                marker=dict(symbol='circle', size=10, color='yellow'),
                showlegend=False
            ))

    fig.update_layout(
        title='TSLA Stock Price with Support/Resistance Bands',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        showlegend=True,
        height=800,
        xaxis=dict(rangeslider=dict(visible=True), type='date')
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

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Start Animation"):
                    st.session_state.stop_animation = False
                    st.session_state.animation_running = True
                if st.button("Stop Animation"):
                    st.session_state.stop_animation = True
                    st.session_state.animation_running = False

            chart_placeholder = st.empty()

            if st.session_state.animation_running:
                # Run the animation loop without rerunning the app
                for i in range(10, len(df) + 1):
                    if st.session_state.stop_animation:
                        break
                    fig = create_candlestick_chart(df.iloc[:i])
                    chart_placeholder.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.2)  # Adjust speed here (slower = smoother)
                st.session_state.animation_running = False
            else:
                fig = create_candlestick_chart(df)
                chart_placeholder.plotly_chart(fig, use_container_width=True)

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
        chatbot = get_chatbot()

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
            st.experimental_rerun()  # Only rerun after chat input, not during animation

if __name__ == "__main__":
    main()
