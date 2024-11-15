from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import slack_sdk # `import slack` is deprecated now
from slack_sdk.errors import SlackApiError
# import argparse
# from argparse import Namespace
import os
import logging

# from apscheduler.schedulers.blocking import BlockingScheduler #schedule tasks
# import threading # need to include threading otherwise you cannot put them together
# user file
from utils import yt_process, chatbot, wiki, gemini
from database import db
from config import *


# set up the bot at the start

logging.basicConfig(filename='mybot.log', level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


processed_messages = set()
app = App(token=SLACK_BOT_TOKEN)
client = slack_sdk.WebClient(token = SLACK_BOT_TOKEN)

BOT_ID = client.api_call("auth.test")["user_id"]

channels = client.conversations_list()
for channel in channels["channels"]:
    if channel["name"] == CHANNEL_NAME:
        CHANNEL_ID = channel["id"]



def _file_upload(file_path, channel_id):
    # Upload the file to the channel
    try:
        response = client.files_upload_v2( # use v2
            channels=channel_id,
            file=file_path,
            title=file_path
            # initial_comment="Here's a file I wanted to share with you!"
        )
        logging.info(f"File uploaded: {response['file']['permalink']}")
    except SlackApiError as e:
        logging.info(f"Error uploading file: {e}")



def file_upload_secure(file_path, channel_id):
    file_size = os.path.getsize(file_path) / 1024 / 1024
    client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"The download succeeded. The file size is{file_size: .2f} MB")
    for i in range(5):
        try:
            _file_upload(file_path, channel_id) 
            logging.info("Slack API request succeeded")
            break
        except Exception as e:
            logging.info("Slack API request failed:", e)
    else:
        logging.info("Slack API request failed after 5 attempts")
    # delete file afterwards whatever it is
    if(os.path.exists(file_path)):
        os.remove(file_path)




help_info = '''
# bot behaviors\n
# `/chat`: chat with openai\n
# `/get_video`: download video and upload to slack (input: yt link)\n
# `/transcribe`: transcribe a video and give you text file (input: yt link)\n
# `/summarize`: summarize a video based on its subtitle files, not all will work (input: yt link)\n
# `/search_video`: search yt video (link, description, uploader) based on keywords\n
# `/web_search`: search the web by using google\n
# `/wiki`: get wiki page based on keyword (must be in correct wiki format)\n
#\n
# probably merge them\n
# `/get_audio`: download audio based on url and upload to slack (same as /get_video)\n
# `/chat_nosave`: same with /chat but do not store any history in db\n
# `/gemini`: request gemini api\n
# `/gpt4`: request GPT-4 turbo api\n
'''
alert_text = '''
(Remember: Both Gemini Pro api and GPT-4 Turbo are all still in expriemental phrase,
so their api references may experience changes and thus would make code here unable to 
function as espected. You may need to check the code constantly and refer to the related
documentations provided by Openai and Google when needed.)
\n
GPT-4 and Gemini Pro api are only avaliable now in no save mode
GPT-4 turbo api may take longer (20-35 seconds) to respond, be patient
\n
\n
'''


@app.command("/chat")
def start_chatbot(ack, respond, command):
    # init the ack and retrieve info
    ack()
    user_prompt = command["text"]
    user_id = command["user_id"]
    trigger_id = command["trigger_id"]

    if user_id != BOT_ID and trigger_id not in processed_messages:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "**start requesting openai**")
        # search session id
        session_id = db.search_session(user_id)
        chat_history = db.make_query(session_id)
        # check if summarization
        chat_history = db.check_summarization(chat_history, session_id, user_id)
        # add prompt to chat history
        chat_history.append({"role": "user", "content": user_prompt})
        res, token_used = chatbot.make_request(chat_history)
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = res["content"])
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"You used {token_used} tokens in this session")

        processed_messages.add(trigger_id)
        # save res to history
        db.insert_data(session_id, user_id, user_prompt, res["content"])
        if len(processed_messages) >= 1000:
            processed_messages.clear()


@app.command("/get_video")
def get_video(ack, respond, command):
    ack()
    user_prompt = command["text"]
    video_name = yt_process.download_video(user_prompt, "18", False) #18: 360p
    if video_name:
        file_upload_secure(video_name, CHANNEL_ID)
    else:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "Please only enter 1 url at time and make sure your url is valid")


# merge this later only here for testing
@app.command("/get_audio")
def get_audio(ack, respond, command):
    ack()
    user_prompt = command["text"]
    video_name = yt_process.download_video(user_prompt, "18", True) #18: does not matter
    if video_name:
        file_upload_secure(video_name, CHANNEL_ID)
    else:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "Please make sure to enter only one URL at a time, and ensure that the URL is valid.")



# merge this as well, only use it now for testing purposes
@app.command("/chat_nosave")
def start_chat_nosave(ack, respond, command):
    # init the ack and retrieve info
    ack()
    user_prompt = command["text"]
    user_id = command["user_id"]
    trigger_id = command["trigger_id"]
    if user_id != BOT_ID and trigger_id not in processed_messages:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "**Start requesting openai (no save mode) **")

        chat_history = [{"role": "user", "content": user_prompt}]
        res, token_used = chatbot.make_request(chat_history, max_tokens= 1200)
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = res["content"])
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"You used {token_used} tokens in this session")
        processed_messages.add(trigger_id)
        if len(processed_messages) >= 1000:
            processed_messages.clear()



@app.command("/transcribe")
def get_transcribe(ack, respond, command):
    ack()
    user_prompt = command["text"]
    transcribe_file = yt_process.download_transcribe(user_prompt)
    if transcribe_file:
        file_upload_secure(transcribe_file, CHANNEL_ID)
    else:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "Please make sure to enter only one URL at a time, and ensure that the URL is valid.")


@app.command("/summarize")
def get_summarization(ack, respond, command):
    ack()
    user_prompt = command["text"]
    caption_str = yt_process.transcribe_text(user_prompt)
    # send caption_str to openai for summarization
    caption_gpt = [{"role": "user", "content": caption_str}]

    res, token_used = chatbot.make_request(caption_gpt, SUMMARIZE_PROMPT)
    client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"{res} and token_used is {token_used}")


# not tested yet!
@app.command("/search_video")
def get_video_result(ack, respond, command):
    ack()
    user_prompt = command["text"]
    res = yt_process.search_youtube(user_prompt)
    processed_search = '\n\n'.join(
        [f"url: {each['url']} \ntitle: {each['title']} \nuploader: {each['uploader']} \nduration: {each['duration']} \nviews: {each['views']}" for each in res])
    client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"{processed_search}")



@app.command("/web_search")
def get_web_result(ack, respond, command):
    ack()
    user_prompt = command["text"]
    res = yt_process.make_google_search(user_prompt)
    processed_search = '\n\n'.join(
        [f"Title: {each['title']} \nLink: {each['link']} \nSnippet: {each['snippet']}" for each in res])
    client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"{processed_search}")



@app.command("/wiki")
def get_wiki_page(ack, respond, command):
    ack()
    user_prompt = command["text"]
    try:
        summary, res = wiki.retrieve_page(user_prompt)
    except:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"Your keyword is not found, kw: {user_prompt}")
    else:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"{summary}")
        # upload html as well
        html_file = wiki.render_wiki_html(res, user_prompt)
        file_upload_secure(html_file, CHANNEL_ID)



## newly added code (starts here)
## you may need to change them later if needed
@app.command("/gemini")
def start_gemini(ack, respond, command):
    # init the ack and retrieve info
    ack()
    user_prompt = command["text"]
    user_id = command["user_id"]
    trigger_id = command["trigger_id"]
    if user_id != BOT_ID and trigger_id not in processed_messages:
        # code above are all the same, copied them from the other function
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "** Start requesting Gemini**")

        res = gemini.make_request(user_prompt)
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = res)
        # prevent repeated messages
        # processed_messages.add(trigger_id)
        # if len(processed_messages) >= 1000:
        #     processed_messages.clear()


@app.command("/gpt4")
def start_gemini(ack, respond, command):
    # init the ack and retrieve info
    ack()
    user_prompt = command["text"]
    user_id = command["user_id"]
    trigger_id = command["trigger_id"]
    if user_id != BOT_ID and trigger_id not in processed_messages:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = "**Start requesting openai (no save mode) **")

        chat_history = [{"role": "user", "content": user_prompt}]
        res, token_used = chatbot.make_request_gpt4(chat_history, max_tokens= 1200)

        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = res["content"])
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"You used {token_used} tokens in this session")
        processed_messages.add(trigger_id)
        if len(processed_messages) >= 1000:
            processed_messages.clear()




@app.command("/help")
def display_help_info(ack, respond, command):
    ack()
    client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"{help_info}")


## ??? 
@app.command("/retrieve_history")
def get_transcribe(ack, respond, command):
    ack()
    user_id = command["user_id"]
    session_id = db.search_session(user_id)
    file_name = f"{session_id}.json"
    if (os.path.exists(file_name)):
        file_upload_secure(file_name, CHANNEL_ID)
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"Successful deleted your history on server. Session: {session_id}")
    else:
        client.chat_postMessage(channel=f"#{CHANNEL_NAME}", text = f"No related json file can be found!")

    






# only use this function to test functionalities, do not use it for other purposes
# delete it when you finished testing all those parts related to this bot
@app.command("/test")
def get_wiki_page(ack, respond, command):
    ack()
    logging.info(command)


# handle message and nothing else
@app.event("message")
def handle_message_events(body, logger):
    logger.info(f'{body["event"]["user"]}: {body["event"]["text"]}')
    


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()