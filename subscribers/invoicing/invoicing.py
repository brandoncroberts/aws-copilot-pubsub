import os
import sys
import json
import boto3
import logging
import pyfiglet


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
slant = pyfiglet.Figlet(font='slant')
aws_region = os.getenv("AWS_DEFAULT_REGION", default='eu-west-1')
sqs_client = boto3.client('sqs', region_name=aws_region)

def get_messages(uri):
    messages = sqs_client.receive_message(QueueUrl=uri, 
                                          WaitTimeSeconds=5)
    
    return messages.get('Messages', [])

def delete_message(queue_uri, receipt):
    try:
        return sqs_client.delete_message(QueueUrl=queue_uri, 
                                         ReceiptHandle=receipt)
    except boto3.ClientError:
        logging.exception(f'Error deleting the message from {queue_uri}')
    
def process_message():
    queue_uri = os.environ.get('COPILOT_QUEUE_URI')
    
    # Process messages
    for message in get_messages(queue_uri):
        
        # Print out the name  with a slanted effect
        message_body = json.loads(message['Body'])['Message']
        customer_name = json.loads(message_body)['customer']
        logging.info('Processing order for: \n')
        logging.info('\n' + slant.renderText(customer_name))
        
        # Message is processed, delete it from the queue
        delete_message(queue_uri, message.get('ReceiptHandle'))
        

if __name__ == '__main__':
    while True:
        process_message()