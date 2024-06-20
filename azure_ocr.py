
import requests
import json
import cv2
import numpy as np
import skimage.io
import os
from dotenv import load_dotenv

load_dotenv()
OCP_APIM_SUBSCRIPTION_KEY = os.getenv("OCP_APIM_SUBSCRIPTION_KEY")

from PIL import Image
from io import BytesIO

def run_azure_ocr(img):
    headers = {
        'Ocp-Apim-Subscription-Key': OCP_APIM_SUBSCRIPTION_KEY,
        'Content-Type': 'application/octet-stream',
    }

    params = (
    ('features', 'read'),
    ('model-version', 'latest'),
    ('language', 'en'),
    ('api-version', '2023-02-01-preview'),
    )

    outputs = []

    # data = json.dumps({'url': url}) # If from URLs on AWS, etc.
    
    # Convert the image to HSV color space 
    bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # Define range of blue color in HSV, for the iOS screenshot format
    lower_blue = np.array([100, 0, 200])
    upper_blue = np.array([140, 150, 255])

    # filter our image to this color range
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Use this mask to layer on original image to create bitwise_and mask
    result_img_hsv = cv2.bitwise_and(hsv, hsv, mask= mask)

    # Apply grayscale for OCR purposes
    result_img_gray = cv2.cvtColor(np.invert(result_img_hsv), cv2.COLOR_BGR2GRAY)

    result_encoded = cv2.imencode('.jpg', result_img_gray)[1]
    
    to_bytes = result_encoded.tobytes()

    image_data = to_bytes 


    # TO SEE IMAGE THAT'S BEING SENT
        # img_from_array = Image.fromarray(result_img_gray) # gives a PIL image
        # img_from_array.show()
  

    response = requests.post('https://takara-test-v0-1.cognitiveservices.azure.com/computervision/imageanalysis:analyze?features=read&model-version=latest&language=en&api-version=2023-02-01-preview', headers=headers, data=image_data)

    if response.status_code == 200:
        print("Request was successful!")
        parsed_response = json.loads(response.text)
        # json_response = json.dumps(parsed_response, indent=4) 
        text_dump = parsed_response.get('readResult',{}).get('content',{})
        lines = text_dump.splitlines()  
        lines = [line for line in lines if line.strip()]
        outputs.append(lines)
        single_string = ' '.join(lines)
        #print(single_string)

    else:
        print(f"Failed to make the request. Status code: {response.status_code}")

    # print("AZURE HERE! ---------------------", single_string)
    return single_string


# https://portal.azure.com/#@stankuboigmail.onmicrosoft.com/resource/subscriptions/81037acb-28c4-4ba0-9628-99c24515b350/resourceGroups/takara/providers/Microsoft.CognitiveServices/accounts/takara-test-v0-1/overview
# https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/quickstarts-sdk/image-analysis-client-library-40?tabs=visual-studio%2Clinux&pivots=programming-language-rest-api
# https://eastus.dev.cognitive.microsoft.com/docs/services/unified-vision-apis-public-preview-2023-04-01-preview/operations/61d65934cd35050c20f73ab6
