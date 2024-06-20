import numpy as np
import cv2
import streamlit as st
import pytesseract
import os
from skimage.util import img_as_ubyte
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'


def highlight_text_areas(image_file):
    # Load the image
    img = image_file

    # Convert the image to HSV color space 
    bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # Define range of blue color in HSV, for the iOS screenshot format
    lower_blue = np.array([100, 0, 200])
    upper_blue = np.array([140, 150, 255])
         # using color map, HSV values may be...
            # Hue: around 100 to 120 (approximately corresponding to 240 to 270 degrees on the color wheel, e.g. more cyan, less deep blues)
                # adjusted from normal degrees because openCV will normalize H to 0 - 180
            # Saturation: relatively low, around 50 to 150
            # Value: high, maybe around 200 to 255
            # use (`color_picker_hsv.py`) to calc bounds

    # filter our image to this color range
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

 
    # Use this mask to layer on original image to create bitwise_and mask
    result_img_hsv = cv2.bitwise_and(hsv, hsv, mask= mask)
        # this is done on a pixel-by-pixel basis. 
            # we look at each pixel in the image
            # if the corresponding pixel in the mask is zero, that means it's not in the blue region
                # so the output pixel in the result is set to zero (black)
            # Otherwise, the original pixel value is retained, because we want to keep that part of the image

    # Apply grayscale for OCR purposes
    result_img_gray = cv2.cvtColor(np.invert(result_img_hsv), cv2.COLOR_BGR2GRAY)
    # result_img_gray = cv2.bitwise_not(result_img_gray)
        # to increase legibility, apply inversion

    ubyte_img = img_as_ubyte(result_img_gray)

    # Extract the bottom portion for URL detection (assuming a 10% slice from the bottom)
    height, width = img.shape[:2]
    bottom_slice = img[int(height * 0.87):, :]

    return ubyte_img, bottom_slice

    # text = pytesseract.image_to_string(highlighted_text, lang='eng')
    # text = os.linesep.join([s for s in text.splitlines() if s])
    # text = text.replace("  "," ")
    # st.write(text)
    # print('found this text for ya in identify_highlights.py', text)
    # return text

#    # Find contours in the mask
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Draw rectangles around the detected highlighted areas
#     for contour in contours:
#         x, y, w, h = cv2.boundingRect(contour)
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

#     # Show the result
#     cv2.imshow('Highlighted Text Areas', highlighted_text)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


def extract_text(highlighted_text_image):
    print("tesseract is now starting--", highlighted_text_image)

    img_from_array = Image.fromarray(highlighted_text_image) # gives a PIL image
    #img_from_array.show()

    text = pytesseract.image_to_string(img_from_array, lang='eng')

    #Clean up text for special chars, etc.
    text = re.sub(r'[|#%\^*\(\)\[\]\{\}"\',<>\\\/]', '', text)

    text = os.linesep.join([s for s in text.splitlines() if s])
    text = text.replace("\n", " ")
    text = re.sub(' +', ' ', text).strip()

    # Remove the first word since it's usually cut-off
    text = ' '.join(text.split()[1:])

    print("text found is ", text)

    return text

def extract_url(bottom_image):
    text = pytesseract.image_to_string(bottom_image, lang='eng')

    img_from_array = Image.fromarray(bottom_image) # gives a PIL image
    # img_from_array.show()

    url_pattern = re.compile(r'\b\S+\.com\b')

    lines = text.splitlines()

    for line in lines:
        match = url_pattern.search(line)
        if match:
            print("match found: ", match.group().strip())
            return match.group().strip()
    return None

# print(text)

# extract_text(highlight_text_areas(cv2.imread('/Users/kuboi/iLightOCR_2024/ios_article_2.PNG')))
# highlight_text_areas(cv2.imread('/Users/kuboi/iLightOCR_2024/ios_article_2.PNG'))