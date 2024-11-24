import json
import os
import boto3
from pytube import YouTube
from youtube_comment_downloader import *
from youtube_transcript_api import YouTubeTranscriptApi
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = 'S3_NAME'
DYNAMODB_TABLE = 'DYNAMO_TABLE_NMAE'

def check_existing_analysis(video_id):
    """check if video analysis already exists in the dynamo db table"""
    table = dynamodb.Table(DYNAMODB_TABLE)
    
    try:
        response = table.get_item(
            Key={'video_id': video_id}
        )
        return 'Item' in response
    except Exception as e:
        logger.error(f"Error checking DynamoDB: {str(e)}")
        return False

def get_video_metadata(url):
    """fetch video metadata using pytube"""
    try:
        yt = YouTube(url)
        
        return {
            'video_id': yt.video_id,
            'title': yt.title,
            'channel_title': yt.author,
            'view_count': yt.views,
            'length': yt.length,
        }
    except Exception as e:
        logger.error(f"Error fetching video metadata: {str(e)}")
        raise

def get_video_comments(url, max_comments=100):
    """fetch video comments using youtube-comment-downloader"""
    comments = []
    try:
        downloader = YoutubeCommentDownloader()
        comment_generator = downloader.get_comments_from_url(url)
        
        for comment in comment_generator:
            if len(comments) >= max_comments:
                break
                
            # Extract only relevant fields
            comments.append({
                'text': comment.get('text', ''),
                'author': comment.get('author', ''),
                'published_at': comment.get('time', ''),
                'like_count': comment.get('likes', 0),
                'reply_count': comment.get('reply_count', 0)
            })
        
        return comments
    except Exception as e:
        logger.error(f"Error fetching video comments: {str(e)}")
        return comments

def get_video_transcript(video_id):
    """fetch video transcript"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Just concatenate all text pieces with spaces
        full_text = ' '.join(entry['text'] for entry in transcript_list)
        return full_text
    except Exception as e:
        logger.warning(f"Error fetching transcript: {str(e)}")
        return None

def save_to_s3(video_id, data):
    """save the collected data to s3"""
    try:
        s3_key = f'{video_id}/video_data.json'
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(data, default=str),
            ContentType='application/json'
        )
        return s3_key
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        raise

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        video_url = body.get('video_url')
        
        if not video_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No video URL provided'})
            }
        
        # get video metadata to get video id
        video_metadata = get_video_metadata(video_url)
        video_id = video_metadata['video_id']
        
        # check if analysis already exists
        if check_existing_analysis(video_id):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Analysis already exists',
                    'video_id': video_id,
                    'status': 'exists'
                })
            }
        
        # fetch video comments
        video_comments = get_video_comments(video_url)

        video_transcript = get_video_transcript(video_id)
        
        # combine all data
        video_data = {
            'metadata': video_metadata,
            'comments': video_comments,
            'transcript': video_transcript,
            'collected_at': datetime.utcnow().isoformat()
        }
        
        # save to S3
        s3_key = save_to_s3(video_id, video_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data collection successful',
                'video_id': video_id,
                's3_key': s3_key,
                'status': 'new'
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }