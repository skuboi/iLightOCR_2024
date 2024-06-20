### IMPORTS ###
import boto3
from pprint import pprint
import pathlib
import os
from io import StringIO
from dotenv import load_dotenv

load_dotenv()
BUCKET_NAME = os.getenv("BUCKET_NAME")

### CONFIGURE BUCKETS ###
s3 = boto3.client("s3")
bucket_name = BUCKET_NAME
aws_urls = []


### FUNCTIONS ###
def upload_file_using_client(my_file):
     # example: uploads file to s3 bucket using the s3 client object
     object_name = "sample_img.png"
     file_name = my_file
     # file_name = os.path.join(pathlib.Path(__file__).parent.resolve(),"sample.txt")
     response = s3.upload_fileobj(file_name, bucket_name, object_name)
     pprint(response)

def mass_upload_aws(my_uploads):
     # Takes the user uploads from st.file_uploader()
    for uploaded_screenshot in my_uploads:
        temp_name = uploaded_screenshot.name
        s3.upload_fileobj(uploaded_screenshot, bucket_name, "iLightUpload_{0}".format(temp_name))
        aws_url = "https://ilightocr-1.s3.us-west-1.amazonaws.com/iLightUpload_{0}".format(temp_name)
        aws_urls.append(aws_url)
        print(aws_url)
    
