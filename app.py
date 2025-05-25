import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from chatbot import TSLChatbot
import time

# Set Streamlit page config
st.set_page_config(
    page_title="TSLA Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'animation_index' not in st.session_state:
    st.session_state.animation_index = 10
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False

@st.cache_resource
def get_chatbot():
    return TSLChatbot()

def create_candlestick_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='TSLA'
    ))
    fig.update_layout(
        title='TSLA Stock Price with Support/Resistance Bands',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        height=800
    )
    return fig

def main():
    st.title("📈 TSLA Stock Analysis Dashboard")

    tab1, tab2 = st.tabs(["Chart Analysis", "AI Assistant"])

    chatbot = get_chatbot()
    df = chatbot.df

    with tab1:
        st.subheader("Interactive Chart")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Start Animation"):
                st.session_state.animation_running = True
                st.session_state.animation_index = 10

            if st.button("Stop Animation"):
                st.session_state.animation_running = False

        chart_placeholder = st.empty()

        if st.session_state.animation_running:
            # Animate incrementally with a short delay
            if st.session_state.animation_index < len(df):
                partial_df = df.iloc[:st.session_state.animation_index]
                fig = create_candlestick_chart(partial_df)
                chart_placeholder.plotly_chart(fig, use_container_width=True)

                st.session_state.animation_index += 1

                # Pause to make animation smooth
                time.sleep(0.1)  # Adjust this delay as needed (0.1s = 100ms)

                # Rerun app to update frame
                st.experimental_rerun()
            else:
                st.session_state.animation_running = False
                fig = create_candlestick_chart(df)
                chart_placeholder.plotly_chart(fig, use_container_width=True)
        else:
            # Show full chart when not animating
            fig = create_candlestick_chart(df)
            chart_placeholder.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("AI Assistant")

        example_questions = [
            "What was the highest price in the dataset?",
            "Show me the trading patterns for the last month"
        ]

        for question in example_questions:
            if st.button(question):
                st.session_state.chat_history.append({"role": "user", "content": question})
                response = chatbot.generate_response(question)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.experimental_rerun()

        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"👤 You: {message['content']}")
            else:
                st.write(f"🤖 Bot: {message['content']}")

        user_query = st.text_input("Ask a question about TSLA stock data:")

        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            response = chatbot.generate_response(user_query)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.experimental_rerun()


if __name__ == "__main__":
    main()
