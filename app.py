from flask import Flask, render_template, request
from googleapiclient.discovery import build
import random
import time

app = Flask(__name__)

# تم وضع المفتاح الذي زودتني به هنا
API_KEY = "AIzaSyA5MT34MOeGs5GBaAq7NapIf5_RAox4UYs"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(video_id):
    try:
        comments = []
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100)
        response = request.execute()
        for item in response['items']:
            user = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append(user)
        return comments
    except Exception as e:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    winner = None
    if request.method == 'POST':
        # استخراج ID الفيديو من الرابط أياً كان شكله
        link = request.form.get('video_id', '')
        if "v=" in link:
            video_id = link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in link:
            video_id = link.split("youtu.be/")[1].split("?")[0]
        else:
            video_id = link
            
        comments = get_comments(video_id)
        time.sleep(2) # تأخير درامي قبل إعلان الفائز
        
        if comments:
            winner = random.choice(comments)
        else:
            winner = "خطأ: تأكد من الرابط أو أن التعليقات مغلقة."
            
    return render_template('index.html', winner=winner)

if __name__ == '__main__':
    app.run()
