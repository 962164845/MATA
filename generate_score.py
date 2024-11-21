import requests
import json
import re
import time
from tqdm import tqdm


# Initialize the prompt for the GPT model
prompt = """
Given the label '{label}' and the text below, please extract words from the text that are closely related to the label.
Return the indices of these words in the text as an array and their relevance scores as another array.
Consider the following example:
text: [Tudor Revival architecture, also known as mock Tudor in the UK, first manifested in domestic architecture in the United Kingdom in the latter half of the 19th century.]
label: [architecture]
For the above example, the first word “tudor” and the third word “architecture” are both related to label “architecture”, then I need the output index=[0,2] and scores=[0.5,1], where the output for both index and score is a python list.
The confidence score ranges from 0 to 1


Format the results as follows(the output for both index and score is a python list).And you only need to respond as follows, no extra content:
index: [index1, index2, ...]
scores: [score1, score2, ...]


text:
{para}
"""


url = "https://api2.aigcbest.top/v1/chat/completions"


headers = {
   'Accept': 'application/json',
   'Authorization': 'Bearer APIKEY',
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json'
}


def evaluate_text(label, text):
    try:
        # Debugging: print the label and text to ensure they are correct
        print(f"Label: {label}")
        print(f"Text: {text}")


        # Escape curly braces in the text to prevent KeyError during string formatting
        safe_text = text.replace("{", "{{").replace("}", "}}")


        # Format the prompt with the provided text and label
        formatted_prompt = prompt.format(label=label, para=safe_text)


        # Construct the payload for the API request
        payload = json.dumps({
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            "temperature": 1,
            "max_tokens": 400
        })


        # Make the POST request to the API
        response = requests.post(url, headers=headers, data=payload)


        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received response code {response.status_code}")
            return [], []


        # Parse the response JSON
        response_data = response.json()
        content = response_data['choices'][0]['message']['content'].strip()


        # Print the complete response for debugging
        print("Model response:", content)


        # Use regex to extract indices and scores
        index_match = re.search(r"index: \[(.*?)\]", content)
        scores_match = re.search(r"scores: \[(.*?)\]", content)


        index = []
        scores = []


        if index_match:
            index = list(map(int, index_match.group(1).split(',')))  # Convert to list of integers


        if scores_match:
            scores = list(map(float, scores_match.group(1).split(',')))  # Convert to list of floats


        return index, scores  # Return the extracted indices and scores


    except Exception as e:
        print(f"Error evaluating text: {e}")
        return [], []  # Return empty lists on error


def improve_readability(input_file, output_file):
    # Load existing articles
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)


    # Ensure articles is a list
    if isinstance(articles, dict):
        articles = [articles]


    # Only process the first 10 articles for testing
    # articles = articles[:10]


    # Evaluate each article's text and add extracted indices and scores
    for article in tqdm(articles, desc="Evaluating Articles"):
        label = article.get('label', '')  # Get the label
        text = article.get('text', '')  # Get the text
        index, scores = evaluate_text(label, text)  # Get indices and scores
        article['index'] = index
        article['scores'] = scores
        time.sleep(1)  # Optional delay between requests


    # Save the updated articles with topics to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


# 使用示例
input_file = 'wikipedia_articles.json'  # 输入文件名
output_file = 'wikipedia_articles_score_all.json'  # 输出文件名
improve_readability(input_file, output_file)
