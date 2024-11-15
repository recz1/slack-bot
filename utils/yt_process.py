from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from googleapiclient.discovery import build
import yt_dlp
import re
import os
import requests
from config import GOOGLE_APP_TOKEN, GOOGLE_SEARCH_CX



# only use it to check url
def _ytb_decorator(func):
    def wrapper(*args, **kwargs):
        url = args[0].strip()
        compiled_url = url.split("&")[0]

        pattern = re.compile(r'(^https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+$')
        if pattern.match(compiled_url):
            video_id = re.search(r"(?<=v=)[\w-]+", url).group(0)
            return func(video_id, *args[1:], **kwargs)
        else:
            print("not a valid youtube url: ", url)
    return wrapper
    



@_ytb_decorator
def download_video(url, res, audio):
    # though i named it as url_list, but you should provide a single url
    options = {
        'format': res, # "18": 360p
        'outtmpl': os.path.join('temp', f'{url}.mp4'),
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'max_downloads': 20,
    }

    if audio:
        options['format'] = 'bestaudio/best'
        options['outtmpl'] = os.path.join('temp', f'{url}.mp3')
        options.pop("merge_output_format")

    ytdlp = yt_dlp.YoutubeDL(options)

    ytdlp.download(url)
    return options["outtmpl"]["default"]


@_ytb_decorator
def download_transcribe(url):
    ## video id example: tu-bh_x3ebo, 
    caption = YouTubeTranscriptApi.get_transcript(url)

    formatter = SRTFormatter()
    caption_data = formatter.format_transcript(caption)

    path = os.path.join('temp', f'{url}.srt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(caption_data)
    return path
   

@_ytb_decorator
def transcribe_text(url):
    caption = YouTubeTranscriptApi.get_transcript(url)
    caption_str = ""
    for each in caption:
        caption_str += each["text"] + " "
    return caption_str



def search_youtube(prompt, max_items=5):
    youtube = build('youtube', 'v3', developerKey=GOOGLE_APP_TOKEN)
    # Define search query and search for videos
    search_response = youtube.search().list(
        q=prompt,
        type='video',
        part='id,snippet',
        maxResults=max_items
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_title = search_result['snippet']['title']
        video_uploader = search_result['snippet']['channelTitle']

        # Call the videos().list() method to retrieve video details for the given video ID
        video_response = youtube.videos().list(
            id=video_id,
            part='contentDetails,statistics'
        ).execute()

        # Get the duration of the video
        duration = video_response['items'][0]['contentDetails']['duration'][2:].lower()
        view_count = video_response['items'][0]['statistics']['viewCount']

        videos.append({
            'url': video_url,
            'title': video_title,
            'uploader': video_uploader,
            'duration': duration,
            'views': view_count
        })
    return videos



def make_google_search(keyword):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
    "key": GOOGLE_APP_TOKEN,
    "cx": GOOGLE_SEARCH_CX,
    "q": keyword
    }
    response = requests.get(url, params=params)
    search_results = response.json()["items"]
    fetched_result = [{"title": result["title"], "link": result["link"], "snippet": result["snippet"]} 
                    for result in search_results]
    return fetched_result
