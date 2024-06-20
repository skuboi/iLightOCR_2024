import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_notion_page():
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
                "external": {"url": "{0}".format(aws_urls[0])} 
                    # NEXT TO DO: make this a loop through the array of images, not just the first image
			}
		}
        ]
    }

    data = json.dumps(new_page_data)
    print(data)
    res = requests.request("POST", create_url, headers=headers, data=data)

    print("res code is: ", res.status_code)
    print("res is: ", res.json())
    return res
