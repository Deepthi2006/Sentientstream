import boto3
import json
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

def test_bedrock():
    print("Testing AWS Bedrock Integration...")
    print(f"Region: {os.getenv('AWS_DEFAULT_REGION')}")
    
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime', 
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        prompt = "Hello, are you active?"
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
        
        print(f"Invoking model: {modelId}")
        response = bedrock.invoke_model(
            body=body, 
            modelId=modelId, 
            accept='application/json', 
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        print("SUCCESS: Bedrock Response Received!")
        print(f"Response: {response_body.get('content')[0].get('text')}")
        
    except Exception as e:
        print("ERROR: Bedrock Failed")
        print(f"Error Message: {str(e)}")
        # print(traceback.format_exc()) # Truncating for brevity but keeping message

if __name__ == "__main__":
    test_bedrock()
