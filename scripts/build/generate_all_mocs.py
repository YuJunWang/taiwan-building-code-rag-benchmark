import os
import yaml
import google.generativeai as genai
from time import sleep

# ==========================================
# 請設定您的 Gemini API Key
# 建議將金鑰設定在環境變數中： export GEMINI_API_KEY="your_api_key_here"
# 或者直接在此處寫入字串 (但不建議將金鑰 commit 到版控)
# ==========================================
API_KEY = os.environ.get("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)
    # 使用比較便宜且快速的模型
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("⚠️ 尚未設定 GEMINI_API_KEY，將跳過 LLM 導讀生成，僅產生基礎 MOC 索引。")
    model = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET_DIR = os.path.join(BASE_DIR, "data", "databases", "okf_knowledge")

def extract_yaml_frontmatter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith("---"):
                return {}
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return yaml.safe_load(parts[1]) or {}
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return {}

def generate_chapter_intro(folder_name, articles_info):
    """呼叫 Gemini 生成章節導讀"""
    if not model:
        return "（未設定 API Key，跳過 AI 導讀生成）"
    
    # 建立 Prompt
    articles_text = "\n".join([f"- {title}: {summary}" for title, summary in articles_info])
    prompt = f"""
你是一個專業的台灣建築法規整理助理。
請根據以下目錄名稱以及該目錄下所屬的法條摘要，撰寫一段 100 字左右的「章節導讀 (Chapter Introduction)」。
請客觀、精準地說明這個章節主要在規範什麼、核心重點為何，讓讀者能快速掌握章節全貌。

目錄名稱：{folder_name}
包含法條：
{articles_text}

請直接輸出導讀內容，不需要多餘的開場白。
"""
    try:
        response = model.generate_content(prompt)
        # 避免觸發 API 速率限制 (Rate limit)
        sleep(2)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling LLM for {folder_name}: {e}")
        return "（LLM 導讀生成失敗）"

def process_directory(current_dir):
    folder_name = os.path.basename(current_dir)
    
    # 略過根目錄 (okf_knowledge) 本身
    if current_dir == TARGET_DIR:
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                process_directory(item_path)
        return

    print(f"Processing directory: {current_dir}")
    
    subdirs = []
    articles = []
    articles_info = [] # 傳給 LLM 參考用的 (title, summary)
    
    # 掃描當前目錄的子資料夾與檔案
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path):
            subdirs.append(item)
            # 遞迴處理子目錄
            process_directory(item_path)
        elif item.endswith('.md') and item != '_index.md':
            metadata = extract_yaml_frontmatter(item_path)
            title = metadata.get('title', item.replace('.md', ''))
            summary = metadata.get('summary', '無摘要資訊。')
            articles.append((item, title, summary))
            articles_info.append((title, summary))
            
    # 如果這個資料夾沒有子資料夾也沒有法條，就不產生 _index.md
    if not subdirs and not articles:
        return

    # 生成章節導讀
    intro_text = generate_chapter_intro(folder_name, articles_info)

    # 組裝 _index.md 內容
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
        # 將法條按照名稱排序，通常是 第1條、第2條...
        for filename, title, summary in sorted(articles, key=lambda x: x[1]):
            moc_content += f"- **[{title}]({filename})**: {summary}\n"

    # 寫入 _index.md
    index_path = os.path.join(current_dir, '_index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(moc_content)
        
    print(f"✅ Generated MOC for {folder_name}")

if __name__ == "__main__":
    print(f"=== 開始遞迴建立 OKF MOC 索引 ===")
    print(f"目標目錄: {TARGET_DIR}")
    if API_KEY:
        print("💡 偵測到 GEMINI_API_KEY，將啟用 AI 導讀生成功能 (Model: gemini-1.5-flash)。")
    process_directory(TARGET_DIR)
    print("=== MOC 索引建立完成 ===")
