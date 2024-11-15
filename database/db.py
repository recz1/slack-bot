import contextlib
import sqlite3
import secrets

from utils import chatbot
from config import init_db, RECALL_PROMPT, TABLE_NAME, db_name



conn = init_db()



@contextlib.contextmanager
def db_connection():
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


# example usage:
# with db_connection() as conn:
#     cursor = conn.execute("SELECT * FROM table")
#     ...



def insert_data(session_id, user_id, user_prompt, res):
    with db_connection() as conn:
        conn.execute(f"INSERT INTO {TABLE_NAME} (session_id, user_id, user_prompt, openai_response) VALUES (?, ?, ?, ?)",
                         (session_id, user_id, user_prompt, res))
        conn.commit()



def make_query(session_id):
    with db_connection() as conn:
        cursor = conn.execute(f"SELECT user_prompt, openai_response FROM {TABLE_NAME} WHERE session_id = ? ORDER BY timestamp DESC LIMIT 10", (session_id,))
        results = cursor.fetchall()
        results.reverse()
        gpt_format = []
        for each in results:
            gpt_format.append({"role": "user", "content": each[0]})
            gpt_format.append({"role": "assistant", "content": each[1]})
        # test code
        print("####################################gpformat")
        print(gpt_format)
    return gpt_format



def search_session(user_id):
    with db_connection() as conn:
        cursor = conn.execute('SELECT session_id FROM session WHERE user_id = ?', (user_id,))
        session_id = cursor.fetchone()
        if session_id == None:
            session_id = secrets.token_hex(16)
            conn.execute('INSERT INTO session (user_id, session_id, last_interaction) VALUES (?, ?, datetime("now"))', (user_id, session_id))
            conn.commit()
        else:
            session_id = session_id[0]
        conn.execute('UPDATE session SET last_interaction = datetime("now") WHERE user_id = ?', (user_id,))
        conn.commit()
    return session_id



def check_summarization(chat_history, session_id, user_id):
    if len(chat_history) >= 12:
        # store them to json before deleting it
        chatbot.save_history(chat_history, session_id)

        chat_history.append({"role": "user", "content": RECALL_PROMPT})
        res, token_used = chatbot.make_request(chat_history, max_tokens= 80)

        #debug code(delete!)
        print("#######################################################################")
        print(f"{res}, token used is {token_used}")
        print('''########################################################################\n
              #########################################################################\n
              #########################################################################
              ''')
        # delete all data
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE session_id = ?", (session_id,))
            conn.commit()

        insert_data(session_id, user_id, RECALL_PROMPT, res["content"])
        chat_history = chat_history[-3:] + [res] # or [-3:]? [-1:]
    return chat_history