import base64
import os
import time
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv  # MISSING!


# Set the API key
load_dotenv()  # NEW

# Get the API key from environment
api_key = os.getenv("GEMINI_API_KEY")  # NEW
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in .env or environment!")  # NEW
genai.configure(api_key=api_key)
class TSLChatbot:
    def __init__(self):
        self.df = None
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        self.load_data()

    def load_data(self):
        """Load and preprocess the TSLA data."""
        try:
            self.df = pd.read_csv('TSLA_data - Sheet1.csv')
            # Convert timestamp to datetime
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            # Convert Support and Resistance strings to lists
            self.df['Support'] = self.df['Support'].apply(eval)
            self.df['Resistance'] = self.df['Resistance'].apply(eval)
            print("Data loaded successfully!")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def generate_response(self, user_query):
        """Generate a response based on the user's query."""
        try:
            # Convert DataFrame to CSV string
            csv_str = self.df.to_csv(index=False)
            
            # Create the prompt
            prompt = f"""I have loaded the TSLA stock data. The data includes timestamp, trading direction (SHORT/LONG), support and resistance levels, OHLC prices, and volume. 
Here is the data in CSV format:
{csv_str}

Please analyze this data and answer the following question:
{user_query}

Please provide a detailed analysis with specific data points from the CSV. Include relevant statistics, trends, and insights."""

            # Add rate limiting
            time.sleep(1)  # Wait 1 second between requests
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            return response.text

        except Exception as e:
            if "429" in str(e):
                return "Rate limit exceeded. Please wait a minute before trying again."
            return f"Error: {str(e)}"

def main():
    print("Initializing TSLA Chatbot...")
    chatbot = TSLChatbot()
    
    print("\nTSLA Data Chatbot (type 'quit' to exit)")
    print("Ask questions about the TSLA stock data...")
    print("Example questions:")
    print("- What was the highest price in the dataset?")
    print("- Show me the trading patterns for the last month")
    print("- What were the most common support levels?")
    print("- Analyze the volume trends")
    
    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() == 'quit':
            break
            
        response = chatbot.generate_response(user_query)
        print("\nResponse:", response)

if __name__ == "__main__":
    main()
