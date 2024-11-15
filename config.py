import os
from dotenv import load_dotenv
import sqlite3
import openai
import google.generativeai as genai
# from prompts import *

# set all the configs needed for the whole program

load_dotenv()

OPENAI_KEY = os.environ['OPENAI_KEY']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
GOOGLE_APP_TOKEN = os.environ['YOUTUBE_DEV_KEY']
GOOGLE_SEARCH_CX = os.environ['GOOGLE_SEARCH_CX']
GOOGLE_GEMINI_KEY = os.environ['GOOGLE_GEMINI_KEY']

# only for storing prompts, change it if you need
SUMMARIZE_PROMPT = '''Please summarize the following text in less than 200 words. If there are any gibberish and words do not make any sense, ignore them. Try to summarize the rest of the part which you can understand'''
RECALL_PROMPT = "What were we talking about, please include details as well"


openai.api_key = OPENAI_KEY

genai.configure(api_key=GOOGLE_GEMINI_KEY)


# change here if you set anything differently
db_name = 'chat_history.db'
TABLE_NAME = "chat_history"
CHANNEL_NAME = "bot-channel"





# creating database and table
# init(create table if not exist)
def init_db():
    conn = sqlite3.connect(db_name)
    conn.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 session_id TEXT NOT NULL,
                 user_id TEXT NOT NULL,
                 user_prompt TEXT NOT NULL,
                 openai_response TEXT NOT NULL,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS session (
            user_id TEXT PRIMARY KEY,
            session_id TEXT,
            last_interaction TIMESTAMP
        )
    ''')
    conn.commit()
    # return the database connection for me
    return conn