import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import nltk
from nltk.corpus import stopwords
import re
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("CSE_ID")


nltk.download('stopwords')

def correct_text(text):
    blob = TextBlob(text)
    corrected_text = text #str(blob.correct())
    return corrected_text

def google_search(search_term, api_key, cse_id):
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id).execute()
        return res.get('items', [])
    except HttpError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def find_article(exp_domain, snippet_text):
    print("querying google")

    search_domain = exp_domain

    corrected_snippet_text = correct_text(snippet_text)
    cleaned_snippet = re.sub(r'[\'"“”]', '', corrected_snippet_text) # remove quotes
    snippet_words = cleaned_snippet.split() # split back into words

    # Define and filter out stopwords
    stop_words = set(stopwords.words('english')) # Define stopwords
    filtered_snippet = [word for word in snippet_words if word.lower() not in stop_words]

    # Cut words down to ~28 words
    limited_snippet = ' '.join(filtered_snippet[:25]) 

    search_term = f"site:{search_domain} {limited_snippet}"
    print(f"Search term: {search_term}")

    
    search_results = google_search(search_term, API_KEY, CSE_ID)
    # print(f"Search results: {search_results}")
    return search_results[0].get('link', None) if search_results else None

# Test cases:
# results = find_article("site:lennysnewsletter.com", "strong ICs with clear quantitative impacts on users rather than within their company. If I see the terms “Agile expert” or “scrum master”")
# results = find_article("techcrunch.com", "example snippet one")
# results = find_article("site:polygon.com", "'video games however 12 years is a ifetime. The world of indie game development — of all game development — as changed unrecognizably since then and the fates'")
# results = find_article("polygon.com", "site:polygon.com time frustrated Indie Game: Movie’s casting. Immakers chose focus stars making whose success either already established seemed guaranteed hatever drama might surround it. majority don’t sell million copies")
# print('manual results here: ', results)
