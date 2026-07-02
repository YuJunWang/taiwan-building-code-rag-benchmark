# OKF 階段二與階段三：LLM 語意標註與 MOC 總結 (Colab 執行腳本)
# -------------------------------------------------------------------------
# 請在 Google Colab 執行此腳本 (需選擇 T4 GPU 執行階段)
#
# 前置作業：
# 1. 確保已經執行過 json_to_okf_v2.py 產生基礎的 okf_knowledge 資料夾
#    (您可以將本地的 okf_knowledge 資料夾壓縮上傳至 Colab 解壓縮)
# -------------------------------------------------------------------------

import os
import re
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 全域 Tag 收集器
global_tags = {}

# (請在 Colab 另外開一個儲存格安裝套件)

# === 1. 載入模型 (使用 bitsandbytes 進行 4-bit 量化以節省 VRAM) ===
model_id = "Qwen/Qwen2.5-7B-Instruct"
print(f"Loading {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_id, 
    device_map="auto",
    quantization_config=quantization_config
)

def generate_text(prompt, max_new_tokens=256):
    messages = [
        {"role": "system", "content": "你是一個專業的台灣建築法規分析助理。請簡潔、精準地回答。"},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens,
        temperature=0.1, # 降低隨機性
        do_sample=True
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

# === 2. 階段二：處理單一法規的 Summary 與 Tags ===
def process_article(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 解析 YAML Frontmatter
    if not content.startswith("---"): return None
    
    parts = content.split("---", 2)
    if len(parts) < 3: return None
    
    try:
        metadata = yaml.safe_load(parts[1])
    except Exception:
        return None
        
    article_text = parts[2].strip()
    
    # 防止重複執行
    if 'summary' in metadata and 'tags' in metadata:
        return metadata['summary']
        
    print(f"Processing {metadata.get('title')}...")
    
    # Prompt LLM 生成摘要與標籤
    prompt = f"""請閱讀以下建築技術規則條文，並提供：
1. 一句話的核心摘要 (summary)
2. 3到5個口語化關鍵字 (tags)，請用半形逗號分隔

法規內容：
{article_text[:1500]} # 避免超過 context window

請嚴格以下列 JSON 格式輸出：
{{"summary": "你的摘要", "tags": ["標籤1", "標籤2"]}}"""

    response = generate_text(prompt)
    
    # 簡易萃取 JSON (實務上可用 Pydantic 確保輸出格式)
    try:
        import json
        # 尋找第一個 { 與最後一個 }
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            result = json.loads(response[start:end+1])
            metadata['summary'] = result.get('summary', '')
            metadata['tags'] = result.get('tags', [])
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        print(f"Failed to parse LLM output for {filepath}: {response}")
        metadata['summary'] = "摘要生成失敗"
        metadata['tags'] = []
        
    # 寫回 Markdown
    new_yaml = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
    new_content = f"---\n{new_yaml}---\n{article_text}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return metadata.get('summary', ''), metadata.get('tags', [])

# === 3. 階段三：建立 MOC (Map of Content) 索引 ===
def process_directory(dirpath):
    print(f"Building MOC for directory: {dirpath}")
    summaries = []
    
    # 收集該目錄下所有 Markdown 檔案的摘要
    for filename in os.listdir(dirpath):
        if filename.endswith(".md") and filename != "_index.md":
            filepath = os.path.join(dirpath, filename)
            result = process_article(filepath)
            if not result: continue
            
            # 若為 tuple 則解構出 tags
            if isinstance(result, tuple):
                summary, tags = result
            else:
                summary, tags = result, []
                
            # 將檔案路徑加入對應的 Tag 陣列
            for tag in tags:
                if tag not in global_tags:
                    global_tags[tag] = []
                # 紀錄完整的跨章節路徑
                rel_path = os.path.join(os.path.basename(dirpath), filename)
                global_tags[tag].append(rel_path)
                
            if summary:
                summaries.append(f"- {filename.replace('.md', '')}: {summary}")
                
    if not summaries: return
    
    # 請 LLM 撰寫章節導讀
    combined_summaries = "\n".join(summaries)
    prompt = f"""以下是建築法規某個章節/小節內所有條文的摘要清單：

{combined_summaries[:2500]}

請寫一段約 100 字的導讀 (Overview)，概述這個章節的核心規範重點。"""

    overview = generate_text(prompt, max_new_tokens=300)
    
    # 寫入 _index.md
    index_path = os.path.join(dirpath, "_index.md")
    index_content = f"""---
type: "moc"
folder: "{os.path.basename(dirpath)}"
---
# {os.path.basename(dirpath)} 導覽索引

## 章節導讀
{overview}

## 包含條文
{combined_summaries}
"""
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

# === 主程式執行 ===
def main():
    root_dir = "okf_knowledge/建築技術規則建築設計施工編"
    if not os.path.exists(root_dir):
        print("找不到 okf_knowledge 資料夾！請先上傳。")
        return
        
    # 遍歷所有章節資料夾
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            process_directory(item_path)
            
    # 建立主題式 MOC
    print("正在建立跨章節的主題式 MOC (Thematic Indexes)...")
    themes_dir = os.path.join(root_dir, "主題索引")
    os.makedirs(themes_dir, exist_ok=True)
    
    theme_count = 0
    for tag, files in global_tags.items():
        # 只有出現 3 次以上的標籤才建立專屬 MOC
        if len(files) >= 3:
            theme_path = os.path.join(themes_dir, f"_theme_{tag}.md")
            content = f"---\ntype: \"theme_moc\"\ntag: \"{tag}\"\n---\n# 主題：{tag}\n\n## 相關法規連結\n"
            for f in files:
                # 建立 Obsidian 格式的內部跨章節連結
                content += f"- [[{f.replace('.md', '')}]]\n"
            
            with open(theme_path, 'w', encoding='utf-8') as out:
                out.write(content)
            theme_count += 1
            
    print(f"成功建立了 {theme_count} 個主題式 MOC！")
    print("OKF 語意標註與 MOC 建置完成！您現在可以將 okf_knowledge 整個資料夾下載回地端了。")

if __name__ == "__main__":
    main()
