# Usage: python scraper.py
# Description: This script - 
# - reads a list of URLs from a file, 
# - scrapes the text content from each URL, 
# - and uses the OpenAI API to summarize the content into structured activity data. 
# - The output is saved as a JSON file.

import requests
from bs4 import BeautifulSoup
import openai
import json
import time
from dotenv import load_dotenv
import os


# Load your OpenAI API key
load_dotenv(override=True)
# openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL_GPT = 'gpt-4o-mini'

def scrape_website(url):
    """Scrape text content from a website"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        return text.strip()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def summarize_content(content):
    """Use OpenAI API to summarize content into structured activity data"""
    if not content:
        return None
    
    prompt = f"Extract main activities from the following text and categorize them as 'sports', 'leisure', or 'culture'. Format the output as a JSON list of objects with 'name' and 'type'.\n\nText: {content}\n\nJSON:"
    
    try:
        response = openai.chat.completions.create(
            model=MODEL_GPT,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        summary = response.choices[0].message.content
        # print(summary)
        return json.loads(summary) if summary else None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def main():
    input_file = "urls.txt"
    output_file = "summaries.json"

    try:
        with open(input_file, "r") as file:
            print("Reading input file complete")
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        # return
        exit
    
    
    results = []
    
    for url in urls:
        print(f"Processing {url}...")
        content = scrape_website(url)
        if content:
            activities = summarize_content(content)
            if activities:
                results.append({"url": url, "data": {"activities": activities}})
    
            print(f"Result of processing {results}")
        time.sleep(2)  # Avoid rate limits
    
    with open(output_file, "w") as file:
        json.dump({"result": results}, file, indent=4)
    
    print(f"Summaries saved to {output_file}")

if __name__ == "__main__":
    main()