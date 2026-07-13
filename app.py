from flask import Flask, render_template, request
from googleapiclient.discovery import build
import random

app = Flask(__name__)
API_KEY = "AIzaSyA5MT34MOeGs5GBaAq7NapIf5_RAox4UYs"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(video_id):
    comments = []
    try:
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100)
        response = request.execute()
        for item in response['items']:
            user = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append(user)
    except:
        return []
    return comments

@app.route('/', methods=['GET', 'POST'])
def index():
    winner = None
    if request.method == 'POST':
        video_id = request.form.get('video_id')
        all_comments = get_comments(video_id)
        if all_comments:
            winner = random.choice(all_comments)
        else:
            winner = "لم يتم العثور على تعليقات!"
    return render_template('index.html', winner=winner)

if __name__ == '__main__':
    app.run(debug=True)
