import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv
from chatbot import TSLChatbot  # Your existing chatbot module
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

# Initialize the chatbot
@st.cache_resource
def get_chatbot():
    api_key_status = "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET"
    print(f"DEBUG: GEMINI_API_KEY status inside get_chatbot: {api_key_status}")
    print(f"DEBUG: GEMINI_API_KEY starts with: {str(os.getenv('GEMINI_API_KEY'))[:5]}...")
    return TSLChatbot()

def create_candlestick_animation(df):
    fig = go.Figure(
        layout=go.Layout(
            title='TSLA Stock Price with Support/Resistance Bands',
            yaxis_title='Price',
            xaxis_title='Date',
            template='plotly_dark',
            height=800,
            xaxis=dict(rangeslider=dict(visible=True), type="date"),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=1.1,
                x=1.05,
                xanchor="right",
                yanchor="top",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, 
                               {"frame": {"duration": 50, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                                "mode": "immediate"}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None],
                               {"frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0}}])
                ]
            )]
        )
    )

    # Add empty traces for initial frame (they will be replaced in frames)
    fig.add_trace(go.Candlestick(x=[], open=[], high=[], low=[], close=[], name='TSLA'))
    fig.add_trace(go.Scatter(x=[], y=[], mode='none', name='Support Band', fill='toself', fillcolor='rgba(0,255,0,0.2)', showlegend=False))
    fig.add_trace(go.Scatter(x=[], y=[], mode='none', name='Resistance Band', fill='toself', fillcolor='rgba(255,0,0,0.2)', showlegend=False))
    fig.add_trace(go.Scatter(x=[], y=[], mode='markers', marker=dict(symbol='triangle-up', size=15, color='green'), name='LONG', showlegend=False))
    fig.add_trace(go.Scatter(x=[], y=[], mode='markers', marker=dict(symbol='triangle-down', size=15, color='red'), name='SHORT', showlegend=False))
    fig.add_trace(go.Scatter(x=[], y=[], mode='markers', marker=dict(symbol='circle', size=10, color='yellow'), name='None', showlegend=False))

    frames = []
    for i in range(10, len(df) + 1):
        df_slice = df.iloc[:i]

        # Candlestick trace
        candle = go.Candlestick(
            x=df_slice['timestamp'],
            open=df_slice['open'],
            high=df_slice['high'],
            low=df_slice['low'],
            close=df_slice['close'],
            name='TSLA'
        )

        # Support band polygon points
        xs_sup = []
        ys_sup_lower = []
        ys_sup_upper = []
        for _, row in df_slice.iterrows():
            if isinstance(row['Support'], list) and len(row['Support']) > 0:
                xs_sup.append(row['timestamp'])
                ys_sup_lower.append(min(row['Support']))
                ys_sup_upper.append(max(row['Support']))
        if xs_sup:
            sup_band = go.Scatter(
                x=xs_sup + xs_sup[::-1],
                y=ys_sup_upper + ys_sup_lower[::-1],
                fill='toself',
                fillcolor='rgba(0,255,0,0.2)',
                line=dict(color='rgba(0,255,0,0)'),
                mode='none',
                showlegend=False
            )
        else:
            sup_band = go.Scatter(x=[], y=[], mode='none')

        # Resistance band polygon points
        xs_res = []
        ys_res_lower = []
        ys_res_upper = []
        for _, row in df_slice.iterrows():
            if isinstance(row['Resistance'], list) and len(row['Resistance']) > 0:
                xs_res.append(row['timestamp'])
                ys_res_lower.append(min(row['Resistance']))
                ys_res_upper.append(max(row['Resistance']))
        if xs_res:
            res_band = go.Scatter(
                x=xs_res + xs_res[::-1],
                y=ys_res_upper + ys_res_lower[::-1],
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,0,0,0)'),
                mode='none',
                showlegend=False
            )
        else:
            res_band = go.Scatter(x=[], y=[], mode='none')

        # Markers for directions
        longs_x, longs_y = [], []
        shorts_x, shorts_y = [], []
        none_x, none_y = [], []

        for _, row in df_slice.iterrows():
            if row['direction'] == 'LONG':
                longs_x.append(row['timestamp'])
                longs_y.append(row['low'] * 0.99)  # green arrow below candle
            elif row['direction'] == 'SHORT':
                shorts_x.append(row['timestamp'])
                shorts_y.append(row['high'] * 1.01)  # red arrow above candle
            else:
                none_x.append(row['timestamp'])
                none_y.append(row['close'])  # yellow circle at close

        long_marker = go.Scatter(x=longs_x, y=longs_y, mode='markers', marker=dict(symbol='triangle-up', size=15, color='green'), showlegend=False)
        short_marker = go.Scatter(x=shorts_x, y=shorts_y, mode='markers', marker=dict(symbol='triangle-down', size=15, color='red'), showlegend=False)
        none_marker = go.Scatter(x=none_x, y=none_y, mode='markers', marker=dict(symbol='circle', size=10, color='yellow'), showlegend=False)

        frames.append(go.Frame(data=[candle, sup_band, res_band, long_marker, short_marker, none_marker], name=str(i)))

    return fig, frames

def main():
    st.title("📈 TSLA Stock Analysis Dashboard")

    tab1, tab2 = st.tabs(["Chart Analysis", "AI Assistant"])

    with tab1:
        st.subheader("Interactive Chart")

        try:
            chatbot = get_chatbot()
            df = chatbot.df

            fig, frames = create_candlestick_animation(df)
            fig.frames = frames

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
            st.experimental_rerun()

if __name__ == "__main__":
    main()
