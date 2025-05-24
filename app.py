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

# Initialize the chatbot
@st.cache_resource
def get_chatbot():
    # Add this print statement
    api_key_status = "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET"
    print(f"DEBUG: GEMINI_API_KEY status inside get_chatbot: {api_key_status}")
    print(f"DEBUG: GEMINI_API_KEY starts with: {str(os.getenv('GEMINI_API_KEY'))[:5]}...")

    return TSLChatbot()

def create_candlestick_chart(df, show_animation=False):
    """Create an interactive candlestick chart with markers and bands"""
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
            # Green up arrow below the candle
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['low'] * 0.99],  # Position below the candle
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=15,
                    color='green'
                ),
                name='LONG',
                showlegend=False
            ))
        elif row['direction'] == 'SHORT':
            # Red down arrow above the candle
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['high'] * 1.01],  # Position above the candle
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=15,
                    color='red'
                ),
                name='SHORT',
                showlegend=False
            ))
        else:
            # Yellow circle for None
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['close']],
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=10,
                    color='yellow'
                ),
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
        height=800
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig

def main():
    st.title("📈 TSLA Stock Analysis Dashboard")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Chart Analysis", "AI Assistant"])
    
    with tab1:
        st.subheader("Interactive Chart")
        
        # Initialize chatbot to get data
        try:
            chatbot = get_chatbot()
            df = chatbot.df  # Get the DataFrame from the chatbot
            
            # Chart controls
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Start Animation"):
                    st.session_state.stop_animation = False # Reset stop flag
                    st.session_state.animation_running = True
                if st.button("Stop Animation"):
                    st.session_state.stop_animation = True # Set stop flag
            
            # Display chart
            if st.session_state.animation_running and not st.session_state.stop_animation:
                # Animation placeholder
                chart_placeholder = st.empty()
                for i in range(10, len(df)+1):
                    if st.session_state.stop_animation:
                         st.session_state.animation_running = False
                         break
                    fig = create_candlestick_chart(df.iloc[:i])
                    chart_placeholder.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.1)
                st.session_state.animation_running = False # Animation finished or stopped
                st.experimental_rerun() # Rerun to show final state and ungrey buttons
            else:
                fig = create_candlestick_chart(df)
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    with tab2:
        st.subheader("AI Assistant")
        
        # Example questions
        example_questions = [
            "What was the highest price in the dataset?",
            "Show me the trading patterns for the last month",
            "What were the most common support levels?",
            "Analyze the volume trends",
            "What was the average trading volume?",
            "Show me the price trend over the last 30 days"
        ]

        # Display example questions as buttons
        st.subheader("Example Questions")
        cols = st.columns(3)
        for i, question in enumerate(example_questions):
            if cols[i % 3].button(question, key=f"btn_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": question})
                response = chatbot.generate_response(question)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Chat interface
        st.subheader("Chat with the Bot")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"👤 You: {message['content']}")
            else:
                st.write(f"🤖 Bot: {message['content']}")

        # Input for new questions
        user_query = st.text_input("Ask a question about TSLA stock data:", key="user_input")
        
        if user_query:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Get bot response
            with st.spinner("Analyzing..."):
                response = chatbot.generate_response(user_query)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Clear the input
            st.rerun()

if __name__ == "__main__":
    main() 