import json
import os
import boto3
import logging

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
        return 'data' in response
    except Exception as e:
        logger.error(f"Error checking DynamoDB: {str(e)}")
        return False

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
