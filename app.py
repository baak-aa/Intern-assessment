import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from chatbot import TSLChatbot

# Set page config
st.set_page_config(
    page_title="TSLA Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

load_dotenv()

@st.cache_resource
def get_chatbot():
    return TSLChatbot()

def create_animated_candlestick(df):
    # Base candlestick for initial frame
    base_candle = go.Candlestick(
        x=df.iloc[:10]['timestamp'],
        open=df.iloc[:10]['open'],
        high=df.iloc[:10]['high'],
        low=df.iloc[:10]['low'],
        close=df.iloc[:10]['close'],
        name='TSLA'
    )
    
    frames = []
    for i in range(10, len(df) + 1):
        frame = go.Frame(
            data=[go.Candlestick(
                x=df.iloc[:i]['timestamp'],
                open=df.iloc[:i]['open'],
                high=df.iloc[:i]['high'],
                low=df.iloc[:i]['low'],
                close=df.iloc[:i]['close'],
            )],
            name=str(i)
        )
        frames.append(frame)
    
    fig = go.Figure(
        data=[base_candle],
        frames=frames,
        layout=go.Layout(
            title='TSLA Stock Price Animation',
            xaxis=dict(rangeslider=dict(visible=True), type='date'),
            yaxis_title='Price',
            template='plotly_dark',
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(
                        label='Play',
                        method='animate',
                        args=[None, {
                            'frame': {'duration': 100, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 0}
                        }]
                    ),
                    dict(
                        label='Pause',
                        method='animate',
                        args=[[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    )
                ],
                x=0.1,
                y=1.1,
                xanchor='right',
                yanchor='top'
            )],
            height=800
        )
    )
    
    # Optionally add support/resistance bands and markers on full data here if needed,
    # but note they won't animate frame-by-frame unless you build frames for those too.
    
    return fig

def main():
    st.title("📈 TSLA Stock Analysis Dashboard")
    
    tab1, tab2 = st.tabs(["Chart Analysis", "AI Assistant"])
    
    with tab1:
        st.subheader("Interactive Chart with Animation")
        try:
            chatbot = get_chatbot()
            df = chatbot.df
            
            fig = create_animated_candlestick(df)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading data: {e}")

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
            st.experimental_rerun()

if __name__ == "__main__":
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    main()
