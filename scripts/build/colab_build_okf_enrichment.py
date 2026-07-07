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
    
    # Prompt LLM 生成摘要與標籤 (加入 One-Shot 範例與繁體中文強約束)
    prompt = f"""請閱讀以下建築技術規則條文，並提供：
1. 一句話的核心摘要 (summary)
2. 3到5個口語化關鍵字 (tags)

【重要指示】
- 必須使用「繁體中文（台灣繁體）」回答，嚴禁使用簡體字。
- 語意摘要請控制在 30-50 字之間，著重於法規的核心義務與規範主體。

【One-Shot 範例】
輸入條文：
第2條：建築基地應與建築線相連接，其連接部份之最小長度應在二公尺以上。基地內私設通路之寬度不得小於左列標準：一、長度未滿十公尺者為二公尺。二、長度在十公尺以上未滿二十公尺者為三公尺。三、長度大於二十公尺為五公尺...

輸出 JSON：
{{"summary": "規範建築基地與建築線連接之最小長度，以及基地內不同長度私設通路之寬度標準。", "tags": ["建築線", "私設通路", "通路寬度", "基地連接"]}}

【本次輸入條文】
{article_text[:1500]}

請嚴格以下列 JSON 格式輸出，不要包含額外的說明文字：
{{"summary": "你的摘要", "tags": ["標籤1", "標籤2"]}}"""

    response = generate_text(prompt)
    
    # 穩健的 JSON 萃取與解析邏輯
    def clean_and_parse_json(json_str):
        # 移去 Markdown Code Block 標記
        json_str = re.sub(r'^```json\s*', '', json_str, flags=re.IGNORECASE)
        json_str = re.sub(r'\s*```$', '', json_str).strip()
        
        # 尋找 JSON 花括號範圍
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON bounds found")
        candidate = json_str[start_idx:end_idx+1]
        
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
            
        # 嘗試修復常見的單引號問題
        try:
            candidate_fixed = re.sub(r"'\s*:\s*", '": ', candidate)
            candidate_fixed = re.sub(r",\s*'", ', "', candidate_fixed)
            candidate_fixed = re.sub(r"{\s*'", '{ "', candidate_fixed)
            candidate_fixed = re.sub(r"'\s*}", '" }', candidate_fixed)
            candidate_fixed = re.sub(r"'\s*,", '" ,', candidate_fixed)
            return json.loads(candidate_fixed)
        except json.JSONDecodeError:
            pass
            
        # 最後的 Regex 萃取手段
        summary_m = re.search(r'"summary"\s*:\s*"([^"]+)"', candidate)
        tags_m = re.search(r'"tags"\s*:\s*\[([^\]]+)\]', candidate)
        res = {}
        if summary_m:
            res['summary'] = summary_m.group(1)
        if tags_m:
            tags_raw = tags_m.group(1)
            res['tags'] = [t.strip().strip('"').strip("'") for t in tags_raw.split(',') if t.strip()]
        if res:
            return res
        raise ValueError("All JSON parsing methods failed")

    try:
        result = clean_and_parse_json(response)
        metadata['summary'] = result.get('summary', '')
        metadata['tags'] = result.get('tags', [])
    except Exception as e:
        print(f"Failed to parse LLM output for {filepath}: {response}. Error: {e}")
        # 使用法規前 100 字作為 Fallback 摘要
        body_clean = re.sub(r'^#\s+.*$', '', article_text, flags=re.MULTILINE).strip()
        fallback_summary = re.sub(r'\s+', ' ', body_clean)[:100].strip()
        if len(body_clean) > 100:
            fallback_summary += "..."
        metadata['summary'] = fallback_summary
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
    subdirs = []
    articles = []
    summaries = []
    
    # 掃描當前目錄的子資料夾與檔案
    for item in os.listdir(dirpath):
        item_path = os.path.join(dirpath, item)
        if os.path.isdir(item_path) and item != "主題索引":
            subdirs.append(item)
        elif item.endswith(".md") and item != "_index.md":
            result = process_article(item_path)
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
                rel_path = os.path.join(os.path.basename(dirpath), item)
                global_tags[tag].append(rel_path)
                
            if summary:
                articles.append((item, summary))
                summaries.append(f"- {item.replace('.md', '')}: {summary}")
                
    # 如果這個資料夾什麼都沒有，就不產生 _index.md
    if not subdirs and not articles:
        return
        
    # 根據內容類型建立導讀 Prompt (加入 One-Shot 範例與繁體中文強約束)
    if articles:
        combined_summaries = "\n".join(summaries)
        prompt = f"""以下是建築法規某個章節/小節內所有條文的摘要清單：
{combined_summaries[:2500]}

請寫一段約 100 字的導讀 (Overview)，概述這個章節的核心規範重點。

【重要指示】
- 必須使用「繁體中文（台灣繁體）」回答，嚴禁使用簡體字。
- 語氣必須專業、客觀且嚴謹。

【One-Shot 範例】
輸入清單：
- 第178條: 規範公園、綠地等公共設施用地地下建築物之適用範圍。
- 第179條: 定義地下建築物、地下使用單元等核心用語。
- 第180條: 規範地下建築物之用途限制與核准程序。

輸出導讀：
本章節主要規範地下建築物之一般設計通則。內容涵蓋地下建築物與公共設施用地的適用範圍、核心技術用語定義，以及地下使用單元的用途限制與核准程序，旨在為地下空間的規劃設計提供基本的法定遵循標準。

【本次輸入清單】
請撰寫此章節之導讀："""
    else:
        combined_subdirs = "\n".join([f"- {d}" for d in subdirs])
        prompt = f"""以下是建築法規某個大章節下包含的子小節目錄：
{combined_subdirs}

請寫一段約 100 字的導讀 (Overview)，概述這個章節的核心規範重點與結構架構。

【重要指示】
- 必須使用「繁體中文（台灣繁體）」回答，嚴禁使用簡體字。
- 語氣必須專業、客觀且嚴謹。

【One-Shot 範例】
輸入目錄：
- 第一節_建築基地
- 第二節_牆面線_建築物突出部份
- 第三節_建築物高度

輸出導讀：
本章節為一般設計通則之系統化規範架構。其下細分為建築基地連接、牆面線退縮與建築物突出物限制、以及建築物高度計算法則等專業章節，旨在針對各別空間機能與構造提供明確的法規導引，以確保建築之整體安全。

【本次輸入目錄】
請撰寫此章節之導讀："""

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
"""

    if subdirs:
        index_content += "\n## 子目錄\n"
        for sd in sorted(subdirs):
            index_content += f"- [[{sd}]]\n"

    if articles:
        index_content += "\n## 包含條文\n"
        # 排序法條
        def get_num_key(art_tuple):
            title = art_tuple[0].replace('.md', '')
            match = re.search(r'\d+', title)
            return int(match.group()) if match else 9999
        
        sorted_articles = sorted(articles, key=get_num_key)
        for filename, summary in sorted_articles:
            title = filename.replace('.md', '')
            index_content += f"- [[{title}]]: {summary}\n"

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"✅ Generated MOC index for {os.path.basename(dirpath)}")

# === 主程式執行 ===
def main():
    root_dir = "okf_knowledge/建築技術規則建築設計施工編"
    if not os.path.exists(root_dir):
        print("找不到 okf_knowledge 資料夾！請先上傳。")
        return
        
    # 深度優先（由深至淺）遞迴遍歷所有子資料夾，確保底層先產生 MOC，上層能順利鏈接
    for root, dirs, files in os.walk(root_dir, topdown=False):
        if "主題索引" in root:
            continue
        process_directory(root)
            
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
