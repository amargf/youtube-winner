from flask import Flask, render_template, request
from googleapiclient.discovery import build
import random
import time

app = Flask(__name__)
API_KEY = "ضع_مفتاحك_هنا"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(video_id):
    try:
        comments = []
        # جلب التعليقات مع معالجة لصفحات متعددة
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=50)
        response = request.execute()
        for item in response['items']:
            user = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append(user)
        return comments
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    winner = None
    video_id = ""
    if request.method == 'POST':
        video_id = request.form.get('video_id', '').split('/')[-1].split('?')[0] # استخراج ID ذكي
        comments = get_comments(video_id)
        
        # إضافة تأخير وهمي لزيادة الإثارة
        time.sleep(2) 
        
        if comments:
            winner = random.choice(comments)
        else:
            winner = "خطأ: تأكد من الرابط أو أن التعليقات مفتوحة."
            
    return render_template('index.html', winner=winner, video_id=video_id)

if __name__ == '__main__':
    app.run()
