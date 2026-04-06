print("DEBUG: Function started")
import json
import os
import boto3
from botocore.exceptions import ClientError
from PIL import Image,ImageDraw, ImageFont
import io
import time
from decimal import Decimal
def lambda_handler(event, context):
    try:
        REGION = event['Records'][0]['awsRegion']
        BUCKET = event['Records'][0]['s3']['bucket']['name']
        OUTPUT_BUCKET = "sofiene-rekognition-project-output-847008502735-us-east-1-an"
        OBJECT_KEY = event['Records'][0]['s3']['object']['key']
        rekognition = boto3.client('rekognition',region_name=REGION)

        request = {
            "Features":["GENERAL_LABELS"],
            "Image":{
                "S3Object":{
                    "Bucket":BUCKET,
                    "Name":OBJECT_KEY
                }
            },
            "MaxLabels":10,
            "MinConfidence":80

        }
        try:
            response = rekognition.detect_labels(**request)
        except ClientError as e:
            print(f"Rekognition API Error: {e.response['Error']['Message']}")


        s3 = boto3.client('s3',region_name=REGION)

        try:
            s3_response = s3.get_object(
                Bucket=BUCKET,
                Key=OBJECT_KEY
                )
            image_binary = s3_response['Body'].read()
            image = Image.open(io.BytesIO(image_binary))
        except Exception as e:
            print(f"Image Processing Error: {e}")



        width,height = image.size

        font_size = max(15,int(height*0.03))
        try:
            font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default(font_size)

        draw = ImageDraw.Draw(image)
        print("DEBUG: Drawing started")
        for label in response['Labels']:
            if 'Instances' in label:
                for instance in label['Instances']:
                    bounding_box = instance['BoundingBox']


                    left = bounding_box['Left']*width
                    top = bounding_box['Top']*height
                    right = left+bounding_box['Width']*width
                    bottom = top+bounding_box['Height']*height

                    
                    text = f"{label['Name']}: {label['Confidence']:.1f}%"

                    text_box = draw.textbbox((left,top-5),text,font=font,font_size=font_size)

                    draw.rectangle([left,top,right,bottom],outline="red",width=4)

                    draw.rectangle(text_box,fill="red")

                    draw.text((text_box[0], max(0,text_box[1]-5)), text, fill="white", font=font)
        print("DEBUG: Drawing ended")

        buffer = io.BytesIO()
        image.save(buffer,format="jpeg")
        buffer.seek(0)
        print("DEBUG: Uploading annotated Image to output bucket")
        s3_upload_response = s3.put_object(Body=buffer,ContentType='image/jpeg',Bucket=OUTPUT_BUCKET,Key=OBJECT_KEY)
        print("DEBUG: Finished uploading annotated image")

        def float_to_decimal(obj):
            if isinstance(obj,list):
                return [float_to_decimal(i) for i in obj]
            elif isinstance(obj,dict):
                return {k:float_to_decimal(v) for k,v in obj.items()}
            elif isinstance(obj,float):
                return Decimal(str(obj))
            return obj
        cleaned_labels = float_to_decimal(response['Labels'])

        try:
            dynamodb = boto3.resource('dynamodb',region_name=REGION)
            table = dynamodb.Table('ImageLabels')
            table.put_item(Item={
                'ImageID':OBJECT_KEY,
                'Labels':cleaned_labels,
                'TimeStamp':int(time.time())
                })
            print("Metadata successfully saved to DynamoDB with Decimal conversion")
        except ClientError as e:
            print(f"DynamoDB Error: {e.response['Error']['Message']}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully Processed")
        }
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sns = boto3.client('sns')
        sns.publish(TopicArn="arn:aws:sns:us-east-1:847008502735:ImageProcessingErrorAlerts",Subject="Pipeline Error:Image labeling",Message=f"🚨 Lambda Error in Image Pipeline!\n\n Error: {str(e)}\n" )


        return {
        'statusCode': 500,
        'body': json.dumps(f"Error processing: {str(e)}")}
