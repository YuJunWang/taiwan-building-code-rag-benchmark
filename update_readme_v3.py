with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace specific lines
content = content.replace('docs/\n│   └── benchmark_v2_report.md', 'docs/\n│   └── benchmark_v3_report.md')
content = content.replace('# 3. 直接執行 V2 評估腳本', '# 3. 直接執行 V3 評估腳本')
content = content.replace('## 🚀 V2 架構升級重點與成果 (V2 Enhancements)', '## 🚀 V3 架構升級重點與成果 (V3 Enhancements)')
content = content.replace('根據初期的實測與 V2 架構評估', '根據初期的實測與 V3 架構評估')
content = content.replace('### 🔍 實際案例解析：V2 雙階段 RAG 實測 (Case Study)', '### 🔍 實際案例解析：V3 雙階段 RAG 實測 (Case Study)')
content = content.replace('為了符合真實世界的 RAG 運作邏輯，V2 測試報告針對', '為了符合真實世界的 RAG 運作邏輯，V3 測試報告針對')
content = content.replace('本次 V2 Benchmark 驗證了 OKF', '本次 V3 Benchmark 驗證了 OKF')

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
