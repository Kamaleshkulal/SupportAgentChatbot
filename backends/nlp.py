# nlp.py
import re
import requests
from bs4 import BeautifulSoup

# Gemini API settings (replace with your actual API key)
API_KEY = 'AIzaSyC5vf57DQG9zOgBF-7UXMfGsWtIKXYUdU8'
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

def generate_response(prompt: str) -> str:
    """
    Sends a POST request to the Gemini API with the provided prompt
    and returns the generated response.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=payload)
    if not response.ok:
        raise Exception("Failed to generate response")
    
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def clean_markdown(text: str) -> str:
    """
    Removes simple Markdown formatting from the provided text.
    """
    text = re.sub(r'#{1,6}\s?', '', text)   
    text = re.sub(r'\*\*', '', text)        
    text = re.sub(r'\n{3,}', '\n\n', text)   
    return text.strip()

def extract_doc_content(doc_url: str, query: str) -> str:
    """
    Fetches the documentation page and returns a snippet of text
    surrounding the query term.
    """
    try:
        response = requests.get(doc_url)
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n")
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 100)
                end = match.end() + 100
                return text[start:end]
            else:
                return "Relevant documentation snippet not found."
        else:
            return "Failed to fetch documentation."
    except Exception as e:
        return f"Error fetching documentation: {str(e)}"
