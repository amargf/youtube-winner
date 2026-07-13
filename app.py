import re
import random
import time
import os
from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# مفتاح API الخاص بي
API_KEY = "AIzaSyA5MT34MOeGs5GBaAq7NapIf5_RAox4UYs"

# تهيئة خدمة YouTube
youtube = build('youtube', 'v3', developerKey=API_KEY)


def extract_video_id(url):
    """
    استخراج video_id من أي نوع من روابط يوتيوب
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/live\/)([\w-]+)',
        r'(?:youtube\.com\/watch\?.*?v=)([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_comments(video_id, max_results=100):
    """
    جلب تعليقات الفيديو مع أسماء المستخدمين
    """
    try:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText'
        )
        response = request.execute()
        
        comments = []
        for item in response.get('items', []):
            # استخراج معلومات التعليق
            snippet = item['snippet']['topLevelComment']['snippet']
            
            # اسم المستخدم (صاحب التعليق)
            author = snippet.get('authorDisplayName', 'مستخدم مجهول')
            
            # نص التعليق
            text = snippet.get('textDisplay', '').strip()
            
            # إضافة معلومات المستخدم مع التعليق
            comments.append({
                'author': author,
                'text': text,
                'full': f"{author}: {text}" if text else author
            })
        
        return comments
        
    except HttpError as e:
        error_reason = e.error_details[0]['reason'] if e.error_details else 'Unknown'
        error_message = e.error_details[0]['message'] if e.error_details else str(e)
        
        if error_reason == 'videoNotFound':
            raise ValueError('الفيديو غير موجود أو تم حذفه')
        elif error_reason == 'commentsDisabled':
            raise ValueError('التعليقات معطلة لهذا الفيديو')
        elif error_reason == 'rateLimitExceeded':
            raise ValueError('تم تجاوز حد الاستخدام اليومي للـ API')
        else:
            raise ValueError(f'خطأ في YouTube API: {error_message}')
    
    except Exception as e:
        raise ValueError(f'حدث خطأ غير متوقع: {str(e)}')


def choose_random_winner(comments):
    """
    اختيار فائز عشوائي من قائمة التعليقات
    """
    if not comments:
        return None
    return random.choice(comments)


@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')


@app.route('/api/pick-winner', methods=['POST'])
def pick_winner():
    """
    API endpoint لاختيار الفائز
    """
    try:
        data = request.get_json()
        video_url = data.get('video_url', '').strip()
        
        if not video_url:
            return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400
        
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'رابط الفيديو غير صالح'}), 400
        
        comments = get_video_comments(video_id)
        
        if not comments:
            return jsonify({'error': 'لا توجد تعليقات لعرضها'}), 404
        
        # محاكاة تأخير لمدة ثانيتين
        time.sleep(2)
        
        # اختيار الفائز
        winner_data = choose_random_winner(comments)
        
        # إرجاع اسم المستخدم مع التعليق
        return jsonify({
            'success': True,
            'winner': winner_data['author'],  # اسم المستخدم فقط
            'winner_comment': winner_data['text'],  # نص التعليق (اختياري)
            'winner_full': winner_data['full'],  # الاسم + التعليق (للنسخ الاحتياطي)
            'total_comments': len(comments)
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'حدث خطأ غير متوقع: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
