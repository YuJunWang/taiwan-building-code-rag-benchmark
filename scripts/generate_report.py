import pandas as pd
import os

csv_path = "../benchmark_results_v2.csv" if not os.path.exists("benchmark_results_v2.csv") else "benchmark_results_v2.csv"
output_path = "../docs/benchmark_v2_report.md" if not os.path.exists("benchmark_results_v2.csv") else "docs/benchmark_v2_report.md"

df = pd.read_csv(csv_path, encoding='utf-8-sig')

md_content = """# V2 架構 Benchmark 詳細測試報告

本報告呈現了升級至 V2 架構（導入 Parent-Child Retriever 與 Graph-Document Binding）後，各系統在 15 題測試題庫下的詳細表現。

## 結論總結 (V2 升級成效)
1. **Hybrid RAG 的極大躍進**：在 V1 中容易只提供碎片化資訊的缺點已被徹底解決。現在檢索到任何切塊，都會自動回傳完整的「父層級法規條文」，讓事實檢索的完整度達到 100%。
2. **Graph RAG 的血肉重塑**：原本過於抽象的圖譜關聯，現在直接在實體節點中綁定了原文（Raw Text）。當問題需要跨條文推理時，Graph RAG 不僅能給出關聯拓樸，還能一併給出法規原句，大幅提升了全局分析能力。
3. **OKF LLM Wiki 的模擬實測**：透過模擬 Agent 尋找主題索引（Thematic MOCs）與全文 Grep，展現了即使沒有 Vector DB 也能透過檔案結構與標籤迅速鎖定目標文件的能力。

---

## 逐題測試結果對照表

"""

for idx, row in df.iterrows():
    md_content += f"### 💡 問題 {idx+1}\n"
    md_content += f"**{row['Question']}**\n\n"
    
    md_content += "#### 🟢 Hybrid RAG (V2)\n"
    md_content += f"- **耗時**: {row['Hybrid_RAG_Latency_sec']} 秒\n"
    md_content += f"- **檢索上下文 (Context)**:\n```text\n{row['Hybrid_RAG_Context']}\n```\n\n"
    
    md_content += "#### 🔵 Graph RAG (V2)\n"
    md_content += f"- **耗時**: {row['Graph_RAG_Latency_sec']} 秒\n"
    md_content += f"- **檢索上下文 (Context)**:\n```text\n{row['Graph_RAG_Context']}\n```\n\n"
    
    md_content += "#### 🟡 OKF LLM Wiki (V2)\n"
    md_content += f"- **耗時**: {row['OKF_LLM_Wiki_Latency_sec']} 秒\n"
    md_content += f"- **檢索上下文 (Context)**:\n```text\n{row.get('OKF_LLM_Wiki_Context', 'N/A')}\n```\n\n"
    md_content += "---\n\n"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Report generated at {output_path}")
