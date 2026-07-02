import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_law(pcode):
    url = f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # The title of the law
    title_tag = soup.find('a', id='hlLawName')
    law_title = title_tag.text.strip() if title_tag else "Unknown_Law"
    print(f"Law Title: {law_title}")

    articles = []
    
    # 尋找所有條文列
    rows = soup.find_all('div', class_='row')
    current_chapter = ""
    
    for row in rows:
        col_no = row.find('div', class_='col-no')
        col_data = row.find('div', class_='col-data')
        
        if col_no and col_data:
            article_no = col_no.text.strip()
            article_text = col_data.text.strip()
            articles.append({
                "chapter": current_chapter,
                "article_no": article_no,
                "content": article_text
            })
        else:
            text = row.text.strip()
            if text and ("編" in text or "章" in text or "節" in text):
                current_chapter = text

    return law_title, articles

def main():
    pcode = "D0070115" # 建築技術規則建築設計施工編
    try:
        law_title, articles = fetch_law(pcode)
        print(f"Total articles parsed: {len(articles)}")
        
        output_file = "building_regulations.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "title": law_title,
                "pcode": pcode,
                "articles": articles
            }, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Error fetching law: {e}")

if __name__ == "__main__":
    main()
