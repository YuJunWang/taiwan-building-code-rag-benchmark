import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = 'https://api.groq.com/openai/v1/models'
headers = {
    'Authorization': f"Bearer {os.getenv('GROQ_API_KEY')}",
    'Content-Type': 'application/json'
}
response = requests.get(url, headers=headers)
models = response.json()
print([m['id'] for m in models.get('data', [])])
