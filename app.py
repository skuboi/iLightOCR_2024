############################################################
############iLightOCR############
############################################################



############################################################

### IMPORTS ###
## Basics ##
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone
import os
import copy
from pprint import pprint
from pathlib import Path
STREAMLIT_SCRIPT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
from io import StringIO

## UI ##
import streamlit as st

## Tesseract ## 
import cv2

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

## Scikit Image ##
import skimage
import skimage.filters
import skimage.io
import skimage.morphology
import skimage.data
import skimage.color
import skimage.util

from skimage.color import rgb2gray
from skimage.filters import threshold_otsu
from skimage.util import img_as_ubyte

## Data & Tools ##
import requests
import re
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

import cv2

## 3P APIs ##
# import openai
import boto3

## Scripts ##
from notion_db import create_notion_page
from aws_upload import mass_upload_aws
from identify_highlights import highlight_text_areas, extract_text, extract_url
from info_calls import *
from search_article_google import *
from azure_ocr import run_azure_ocr

# ENV 
load_dotenv()
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

## AWS ##
s3 = boto3.client("s3")
bucket_name = "ilightocr-1"


if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = ""

############################################################
# NOTION INTEGRATION #
############################################################
# Moved to notion_db.py  
headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_notion_page(notion_title, ai_summary, aws_url):
    print("create notion has been called!")
    create_url = "https://api.notion.com/v1/pages"

    new_page_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": notion_title
                        }
                    }
                ]
            },
            "Summary": {
                "rich_text": [
                    {"text": {
                        "content": ai_summary
                        }
                    }
                ]
            },
            #"URL": { "url": notion_url},
            "Published": {"date": {"start": datetime.now().astimezone(timezone.utc).isoformat(), "end": None}},
        },
        "children": [
		{
			"object": "block",
			"type": "image",
			"image": {
                "type": "external",
                "external": {"url": "{0}".format(aws_url[0])} 
                    # NEXT TO DO: make this a loop through the array of images, not just the first image
			}
		}
        ]
    }

    data = json.dumps(new_page_data)
    print('json data dump: ', data)
    res = requests.request("POST", create_url, headers=headers, data=data)

    print("res code is: ", res.status_code)
    print("res is: ", res.json())
    return res


############################################################
# AWS INTEGRATION #
############################################################
# Need to host images in AWS first before Notion



############################################################
# STREAMLIT INTERFACE #
############################################################

st.title('iLightOCR')
st.subheader("summarize + save article snippets when on-the-go.")
st.divider()

############################################################
# HANDLE UPLOADS #
############################################################
st.subheader("upload your screenshots")
my_img = st.file_uploader('file uploader [png and jpg only]', type = ['png', 'jpg'], accept_multiple_files=True)
my_img_copy = copy.deepcopy(my_img)
my_img_copy_2 = copy.deepcopy(my_img_copy)
my_img_copy_3 = copy.deepcopy(my_img_copy_2)

img_array = []

############################################################

# CHECK IF IMAGE IS SCREENSHOT #

# SEND SCREENSHOTS TO AWS #

############################################################
aws_urls = []
counter = 0

ios_screenshot_dimensions = [
    (750, 1334),  # iPhone 6, 6S, 7, 8
    (1125, 2436), # iPhone X, XS
    (1242, 2688), # iPhone XS Max
    (828, 1792),  # iPhone XR
    (1170, 2532), # iPhone 12, 12 Pro
    (1284, 2778),
    (1179,2556)
]

found_text = []
found_urls = []

def clearing():
    st.write("")

if my_img:
    if st.button("Upload Images for Processing", on_click=clearing()):
        print("Starting a new test now -----------")
        non_sc_flag = False # checks if there are any photos / non-screenshot images

        for uploaded_file_2 in my_img_copy_2:
            img_array.append(skimage.io.imread(uploaded_file_2))

        # for uploaded_file_3 in my_img_copy_3:
        #     # run_azure_ocr(skimage.io.imread(uploaded_file_3))


        # Heuristics on whether it's a screenshot or not    
        for uploaded_file in my_img_copy:
            img = Image.open(uploaded_file)
            exifdata = img._getexif()


            if exifdata:
                has_gps = 0
                is_ios_size = 0
                has_camera_make_model = 0
                has_screenshot_comment = 0

                width, height = img.size
                if (width, height) in ios_screenshot_dimensions:
                    is_ios_size = -1
       
            for tagid in exifdata:
                tagname = TAGS.get(tagid, tagid)
                value = exifdata.get(tagid)
                # print(f"{tagname:25}: {value}")

                if tagname == 'GPSInfo':
                    has_gps = 1
                elif tagname in ['XResolution', 'YResolution']:
                    # You can add further checks for resolution here if needed
                    pass
                elif tagname in ['Make', 'Model']:
                    has_camera_make_model = 1
                elif tagname == 'UserComment' and re.search(r'screenshot', str(value), re.IGNORECASE):
                    has_screenshot_comment = -3
            
            score = has_gps + has_screenshot_comment + has_camera_make_model + is_ios_size

            if score > 0:
                print("image expected to NOT be a screenshot, based on predicted score of ", score)
                non_sc_flag = True
            if score < 0:
                print("image is likely a screenshot, based on predicted score of ", score)
                
        if non_sc_flag == False:
            st.write("uploading images...")
            for uploaded_file in my_img:
                temp_name = uploaded_file.name
                s3.upload_fileobj(uploaded_file, bucket_name, "iLightUpload_{0}".format(temp_name))
                aws_url = "https://ilightocr-1.s3.us-west-1.amazonaws.com/iLightUpload_{0}".format(temp_name)
                aws_urls.append(aws_url)
                print(aws_url)
                counter = counter + 1
                # print(uploaded_file)

            
            
            for uploaded_file in img_array:
                print('trying')
                ubyte_img, bottom_slice = highlight_text_areas(uploaded_file) # now B/W and Ubyte
                # snippet = extract_text(ubyte_img)
                url = extract_url(bottom_slice)

                snippet = run_azure_ocr((uploaded_file))

                article_link = find_article(url, snippet)

                found_text.append(snippet)
                found_urls.append(article_link)
                print("Found URLs here: ", found_urls)

        if non_sc_flag == True:
            st.write("Looks like you uploaded a photo - please remove any non-screenshots and try again")


# Check / user communication step #
if len(aws_urls) > 0:
    if  len(aws_urls) == len(my_img):
        st.write("the number of images you uploaded is: ",len(aws_urls))
        st.write("beginning processing and analysis...")



############################################################
# GET SUMMARIES FROM AI LLMS #
############################################################
ai_summaries = []

if len(found_text) > 0:
    st.write("writing AI summaries...")

    all_together = ' <NEXT SECTION> '.join(found_text) # Combine individual snippets

    answer = gpt_req(all_together) # Send to GPT for summary of all snippets together
    st.session_state.ai_summary = answer

    notion_title = define_title(answer)

    st.write("Article Topic: ", notion_title)
    st.write("Website link: ", article_link)

    # st.write("GPT Summary: ", answer)

    if answer is not None:
       # if st.button("test test notion test"):
        create_notion_page(notion_title, answer, aws_urls)
            

if st.session_state.ai_summary:
    st.write("AI Summary: ", st.session_state.ai_summary)