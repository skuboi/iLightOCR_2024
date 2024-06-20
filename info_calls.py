import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key = openai_key
)


def gpt_req(img_text):
    json_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Summarize the key points from snippets of text from a single article that the user gives you. '...' indicates a transition to a new part of the article."},
            {"role": "user", "content": "Article text snippets: {0}".format(img_text)}
        ]
    )
    # chat_response = json_response["choices"][0]["message"]["content"]
    # st.markdown("GPT3.5 summary: ", chat_response)
    # print(chat_response)
    print(json_response.choices[0].message.content)
    return json_response.choices[0].message.content

# gpt_req("PowerScs a web-based\nplatform that helps educational\ninstitutions manage operations such\nas enrollment, grades, attendance\nand communications with parents\nand students. Founded in 1997 by\nGreg Porter, initially as a student\ninformation system for schools, the\nCompany was acquired by Apple in\n2001 for $62 million in Apple stock")

def master_summary(summaries):
    json_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Summarize an article, given the key points provided. Should be a short overview of the article contents."},
            {"role": "user", "content": "Article key points: {0}".format(summaries)}
        ]
    )
    print(json_response.choices[0].message.content)
    return json_response.choices[0].message.content

def define_title(summaries):
    json_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Propose an article title, given the key points provided."},
            {"role": "user", "content": "Article key points: {0}".format(summaries)}
        ]
    )
    print(json_response.choices[0].message.content)
    return json_response.choices[0].message.content