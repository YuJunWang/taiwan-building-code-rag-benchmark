import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STRUCTURE_JSON = os.path.join(BASE_DIR, "scratch", "okf_structure.json")
TARGET_DIR = os.path.join(BASE_DIR, "data", "databases", "okf_knowledge")

def get_clean_name(folder_name):
    # Remove prefix like "第一章_", "第一節_", "第四章_之_一_"
    clean = re.sub(r'^(第[一二三四五六七八九十百]+[章節編])_*(?:之_*[一二三四五六七八九十百]+_*)?', '', folder_name)
    clean = clean.replace('_', '、')
    return clean

def generate_moc_files():
    if not os.path.exists(STRUCTURE_JSON):
        print(f"Error: {STRUCTURE_JSON} does not exist. Please run dump_okf_structure.py first.")
        return

    with open(STRUCTURE_JSON, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    for rel_path, data in structure.items():
        folder_name = data["folder_name"]
        subdirs = data["subdirs"]
        articles = data["articles"]
        
        # Determine full directory path (normalize path slashes for OS)
        dir_path = os.path.join(TARGET_DIR, rel_path)
        
        clean_name = get_clean_name(folder_name)
        
        # Template-based professional introduction
        if subdirs and not articles:
            intro_text = f"本章節「{folder_name}」為有關{clean_name}之系統化規範架構。其下細分為數個專業章節（如子目錄所示），旨在針對各別機能與構造提供明確的法規導引與技術標準，以確保建築之整體安全與公共福祉。"
        elif articles:
            intro_text = f"本章節「{folder_name}」主要規範{clean_name}之具體設計指標與工程構造標準。本節包含以下相關條文，為建築物的細部規劃、安全防護及行政審查提供明確的法定遵循依據。"
        else:
            intro_text = f"本章節「{folder_name}」收錄了有關{clean_name}之相關規範與技術說明。"

        # Compile _index.md content
        moc_content = f"""---
type: "moc"
folder: "{folder_name}"
---
# {folder_name} 導覽索引

## 章節導讀
{intro_text}
"""

        if subdirs:
            moc_content += "\n## 子目錄 (Sub-Folders)\n"
            for sd in sorted(subdirs):
                moc_content += f"- 📁 **{sd}**\n"

        if articles:
            moc_content += "\n## 包含條文 (Articles)\n"
            # Sort articles by their numerical name if possible, otherwise string sort
            def get_num_key(art):
                title = art["title"]
                match = re.search(r'\d+', title)
                return int(match.group()) if match else 9999
            
            sorted_articles = sorted(articles, key=get_num_key)
            for art in sorted_articles:
                filename = art["filename"]
                title = art["title"]
                summary = art["summary"]
                moc_content += f"- **[{title}]({filename})**: {summary}\n"

        # Write _index.md
        index_path = os.path.join(dir_path, '_index.md')
        try:
            with open(index_path, 'w', encoding='utf-8') as index_file:
                index_file.write(moc_content)
            print(f"Generated MOC for {folder_name}")
        except Exception as e:
            print(f"Error writing to {index_path}: {e}")

if __name__ == "__main__":
    print("=== 開始本地產生 OKF MOC 索引 ===")
    generate_moc_files()
    print("=== MOC 索引產生完成 ===")
