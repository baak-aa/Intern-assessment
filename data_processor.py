import pandas as pd
import numpy as np
from typing import List, Tuple
import ast

def load_tsla_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess TSLA stock data from CSV file
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed dataframe with OHLCV data and indicators
    """
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert timestamp to datetime
    df['Date'] = pd.to_datetime(df['timestamp'])
    
    # Convert column names to match our expected format
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    # Process support and resistance columns
    def process_list_string(x):
        if pd.isna(x) or x == '[]':
            return []
        try:
            # Handle both string and list formats
            if isinstance(x, str):
                # Remove any extra spaces and convert to list
                x = x.replace(' ', '')
                return ast.literal_eval(x)
            return x
        except:
            return []
    
    df['Support'] = df['Support'].apply(process_list_string)
    df['Resistance'] = df['Resistance'].apply(process_list_string)
    
    # Calculate support and resistance bands
    df['Support_Lower'] = df['Support'].apply(lambda x: min(x) if x else np.nan)
    df['Support_Upper'] = df['Support'].apply(lambda x: max(x) if x else np.nan)
    df['Resistance_Lower'] = df['Resistance'].apply(lambda x: min(x) if x else np.nan)
    df['Resistance_Upper'] = df['Resistance'].apply(lambda x: max(x) if x else np.nan)
    
    # Sort by date
    df = df.sort_values('Date')
    
    return df

def calculate_direction_markers(df: pd.DataFrame) -> Tuple[List[float], List[str], List[str]]:
    """
    Calculate marker positions and styles based on direction
    
    Args:
        df (pd.DataFrame): Processed dataframe
        
    Returns:
        Tuple[List[float], List[str], List[str]]: Marker positions, colors, and symbols
    """
    positions = []
    colors = []
    symbols = []
    
    for idx, row in df.iterrows():
        if row['direction'] == 'LONG':
            positions.append(row['Low'] * 0.99)  # Below the candle
            colors.append('green')
            symbols.append('triangle-up')
        elif row['direction'] == 'SHORT':
            positions.append(row['High'] * 1.01)  # Above the candle
            colors.append('red')
            symbols.append('triangle-down')
        else:
            positions.append(row['Close'])
            colors.append('yellow')
            symbols.append('circle')
    
    return positions, colors, symbols

def get_animation_frames(df: pd.DataFrame, frame_duration: int = 100) -> List[dict]:
    """
    Generate animation frames for the chart
    
    Args:
        df (pd.DataFrame): Processed dataframe
        frame_duration (int): Duration of each frame in milliseconds
        
    Returns:
        List[dict]: List of frames for animation
    """
    frames = []
    
    for i in range(1, len(df) + 1):
        frame = {
            'data': df.iloc[:i].to_dict('records'),
            'duration': frame_duration
        }
        frames.append(frame)
    
    return frames 