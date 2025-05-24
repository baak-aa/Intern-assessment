import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from chatbot import TSLChatbot

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
    # Create frames for animation
    frames = []
    n = len(df)
    
    # Pre-build base data for candlestick + markers + bands for initial frame
    def get_candlestick_data(df_slice):
        return go.Candlestick(
            x=df_slice['timestamp'],
            open=df_slice['open'],
            high=df_slice['high'],
            low=df_slice['low'],
            close=df_slice['close'],
            name='TSLA'
        )
    
    def get_markers(df_slice):
        markers = []
        for _, row in df_slice.iterrows():
            if row['direction'] == 'LONG':
                markers.append(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['low'] * 0.99],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=15, color='green'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            elif row['direction'] == 'SHORT':
                markers.append(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['high'] * 1.01],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=15, color='red'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            else:
                markers.append(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['close']],
                    mode='markers',
                    marker=dict(symbol='circle', size=10, color='yellow'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        return markers
    
    def get_support_band(df_slice):
        # Green band for support, per timestamp use min/max from Support list
        xs = []
        ys_lower = []
        ys_upper = []
        for _, row in df_slice.iterrows():
            if isinstance(row['Support'], list) and len(row['Support']) > 0:
                xs.append(row['timestamp'])
                ys_lower.append(min(row['Support']))
                ys_upper.append(max(row['Support']))
        
        if not xs:
            return None
        
        return go.Scatter(
            x=xs + xs[::-1],  # forward + backward for fill
            y=ys_upper + ys_lower[::-1],
            fill='toself',
            fillcolor='rgba(0,255,0,0.2)',  # translucent green
            line=dict(color='rgba(0,255,0,0)'),
            hoverinfo='skip',
            showlegend=False,
            name='Support Band',
            mode='none'
        )
    
    def get_resistance_band(df_slice):
        # Red band for resistance, per timestamp use min/max from Resistance list
        xs = []
        ys_lower = []
        ys_upper = []
        for _, row in df_slice.iterrows():
            if isinstance(row['Resistance'], list) and len(row['Resistance']) > 0:
                xs.append(row['timestamp'])
                ys_lower.append(min(row['Resistance']))
                ys_upper.append(max(row['Resistance']))
        
        if not xs:
            return None
        
        return go.Scatter(
            x=xs + xs[::-1],
            y=ys_upper + ys_lower[::-1],
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',  # translucent red
            line=dict(color='rgba(255,0,0,0)'),
            hoverinfo='skip',
            showlegend=False,
            name='Resistance Band',
            mode='none'
        )
    
    # Initial data (first 10 points or fewer if less data)
    init_slice = df.iloc[:10] if n >= 10 else df
    
    data = [get_candlestick_data(init_slice)]
    data += get_markers(init_slice)
    support_band = get_support_band(init_slice)
    if support_band:
        data.append(support_band)
    resistance_band = get_resistance_band(init_slice)
    if resistance_band:
        data.append(resistance_band)
    
    # Create frames incrementally growing the data slice
    for i in range(11, n + 1):
        df_slice = df.iloc[:i]
        frame_data = [get_candlestick_data(df_slice)]
        frame_data += get_markers(df_slice)
        support_band = get_support_band(df_slice)
        if support_band:
            frame_data.append(support_band)
        resistance_band = get_resistance_band(df_slice)
        if resistance_band:
            frame_data.append(resistance_band)
        frames.append(go.Frame(data=frame_data, name=str(i)))
    
    # Create layout with play/pause buttons with faster response
    layout = go.Layout(
        title='TSLA Stock Price with Support/Resistance and Direction Markers',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        yaxis_title='Price',
        template='plotly_dark',
        height=800,
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            x=0.1,
            y=1.15,
            xanchor='right',
            yanchor='top',
            buttons=[
                dict(
                    label='Play',
                    method='animate',
                    args=[None, {
                        'frame': {'duration': 50, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 0},
                        'mode': 'immediate'
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
            ]
        )]
    )
    
    fig = go.Figure(data=data, frames=frames, layout=layout)
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
