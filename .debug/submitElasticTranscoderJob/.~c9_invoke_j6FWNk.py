from __future__ import print_function


from datetime import datetime
import logging

import json
import urllib
import boto3

print('Loading function')

REGION_NAME = 'ap-southeast-2'
TRANSCODER_ROLE_NAME = 'Elastic_Transcoder_Default_Role'
PIPELINE_NAME = 'autotranscode-pipe'
IN_BUCKET_NAME = 'tommcm-autotranscode-input'
OUT_BUCKET_NAME = 'tommcm-autotranscode-output'
INPUT_KEY = 'D0002022073_00000/sample.mp4'  # e.g. 'D0002021500_00000/sample.mp4'

# logging.basicConfig()  # http://stackoverflow.com/questions/27411778/no-handlers-found-for-logger-main
# logger = logging.getLogger(__name__)

s3 = boto3.client('s3')
transcoder = boto3.client('elastictranscoder', REGION_NAME)

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    INPUT_KEY = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    
    pipelines = transcoder.list_pipelines()
    pipeline_id = str(pipelines['Pipelines'][0]['Id'])
    
    job = transcoder.create_job(
        PipelineId=pipeline_id,
        Input={
            'Key': INPUT_KEY,
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto',
            'Interlaced': 'auto',
            'Container': 'auto',
        },
        Outputs=[
            {
                'Key': 'HLS/1M/{}'.format('.'.join(INPUT_KEY.split('.')[:-1])),
                'PresetId': '1351620000001-200030',  # System preset: HLS 1M
                'SegmentDuration': '10',
            },
        ],
    )
    print("start time={}".format(datetime.now().strftime("%H:%M:%S.%f")[:-3]))
    print("job={}".format(job))
    job_id = job['Job']['Id']
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    
    
    
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
        
    
