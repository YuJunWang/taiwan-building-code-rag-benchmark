import requests
from bs4 import BeautifulSoup
import os
import re

def fetch_and_build_okf():
    url = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title_tag = soup.find('a', id='hlLawName')
    law_title = title_tag.text.strip() if title_tag else "建築技術規則建築設計施工編"

    okf_dir = "okf_knowledge"
    if not os.path.exists(okf_dir):
        os.makedirs(okf_dir)
        
    law_dir = os.path.join(okf_dir, law_title)
    if not os.path.exists(law_dir):
        os.makedirs(law_dir)

    # State tracking
    current_part = ""
    current_chapter = ""
    current_section = ""
    
    # We iterate over all immediate children of the law-reg-content div or just find all relevant divs
    # Usually they are sequential in the DOM
    content_div = soup.find('div', class_='law-reg-content')
    if not content_div:
        print("Failed to find law-reg-content")
        return
        
    articles_count = 0
    articles_data = [] # 儲存 JSON 用
    
    for child in content_div.find_all('div', recursive=False):
        classes = child.get('class', [])
        
        # Is it a chapter/section header?
        if any('h3' in c for c in classes):
            text = child.text.strip()
            # clean up spaces (e.g. "第 一 章 總則" -> "第一章 總則")
            text = re.sub(r'第\s+([一二三四五六七八九十百]+)\s+([編章節])', r'第\1\2', text)
            text = text.replace('  ', ' ') # normalize spaces
            
            if '編' in text:
                current_part = text
                current_chapter = ""
                current_section = ""
            elif '章' in text:
                current_chapter = text
                current_section = ""
            elif '節' in text:
                current_section = text
                
        # Is it an article?
        elif 'row' in classes:
            col_no = child.find('div', class_='col-no')
            col_data = child.find('div', class_='col-data')
            if col_no and col_data:
                article_no = col_no.text.strip()
                # Clean up article no: "本條文有附件 第 23 條" -> "第23條"
                clean_no_match = re.search(r'第\s*\d+(-\d+)?\s*條', article_no)
                clean_no = clean_no_match.group() if clean_no_match else article_no
                clean_no = clean_no.replace(' ', '') # '第23條'
                
                content = col_data.get_text(separator='\n', strip=True)
                
                # Determine folder path
                folder_parts = [law_dir]
                if current_chapter:
                    # e.g. "第一章 總則" -> "第一章_總則"
                    ch_folder = current_chapter.replace(' ', '_').replace('、', '_')
                    folder_parts.append(ch_folder)
                if current_section:
                    sec_folder = current_section.replace(' ', '_').replace('、', '_')
                    folder_parts.append(sec_folder)
                    
                target_dir = os.path.join(*folder_parts)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    
                # Find related articles using Regex
                # Looks for "第 OOO 條" in the content
                related_refs = re.findall(r'第\s*[一二三四五六七八九十百零\d]+(?:之[一二三四五六七八九十百零\d]+|\-\d+)?\s*條', content)
                # Clean up spaces
                related_refs = [r.replace(' ', '') for r in related_refs]
                # Remove duplicates and self-references
                related_refs = list(set([r for r in related_refs if r != clean_no]))
                
                # We can also do string replacement to create markdown links in the content, but for OKF it's tricky 
                # because we don't know the exact relative path if the target is in a different chapter.
                # Just keeping them in YAML `related_articles` is great for Agent search.
                
                md_path = os.path.join(target_dir, f"{clean_no}.md")
                
                yaml_related = "[" + ", ".join(f'"{r}"' for r in related_refs) + "]" if related_refs else "[]"
                
                md_content = f"""---
title: "{clean_no}"
law: "{law_title}"
chapter: "{current_chapter}"
section: "{current_section}"
related_articles: {yaml_related}
---
# {clean_no}

{content}
"""
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                    
                # 收集資料準備匯出給 RAG 使用的 V2 JSON
                articles_data.append({
                    "part": current_part,
                    "chapter": current_chapter,
                    "section": current_section,
                    "article_no": clean_no,
                    "content": content
                })
                    
                articles_count += 1

    # 輸出結構化且保留換行的 JSON 給 RAG 腳本使用
    import json
    with open('building_regulations_v2.json', 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully built OKF structure and saved V2 JSON for {articles_count} articles.")

if __name__ == "__main__":
    fetch_and_build_okf()
