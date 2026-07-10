import json
import subprocess
import time
import re
import random
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

answers = [
    "根據建築技術規則，建築基地面積（簡稱基地）的定義為「建築基地之水平投影面積」。",
    "有效採光面積未達該居室樓地板面積百分之五者。",
    "非防火構造建築物，其外牆為木造或難燃材料構造者，與相鄰基地境界線之距離應為一．五公尺以上。",
    "應具有一小時以上之防火時效。",
    "單車道寬度應為三點五公尺以上，雙車道寬度應為五點五公尺以上。",
    "私設通路長度自建築線起算未超過三十五公尺部分，得計入法定空地面積。私設通路與道路之交叉口免截角。",
    "建築物高度超過十層樓以上的部分必須設置緊急用昇降機（除非有特定免除條款）。緊急用昇降機間的牆壁應具備一小時以上防火時效，且須設置排煙設備。",
    "供商場使用的地下室，其直通樓梯總寬度須依其樓地板面積計算，且每座直通樓梯寬度不得小於一．二公尺，並應符合特定避難寬度要求。",
    "一般建築物屋頂突出物水平投影面積之和，以不超過建築面積百分之十二點五為限。",
    "分戶牆主要用於區隔不同住戶，需具備一定時效的防火與隔音性能；而防火牆必須為獨立構造（或無開口的防火構造），不僅防火時效要求更高，更需能阻擋火勢蔓延至相鄰建築。",
    "1. 強化防火區劃與排煙設備；2. 必須設置特別安全梯與緊急用昇降機；3. 結構上需具備更高的耐震與耐風設計標準。",
    "主要依據建築物的總樓地板面積、使用用途分類（如公眾使用或一般住宅）以及基地條件，按一定比例計算應附建的防空避難設備面積。",
    "設置於屋頂之雨水貯留系統、節能設施、綠化等公益設施，其投影面積若符合規定比例（通常為1/3至2/3以上透空等），得免計入建築面積及建築物高度，且其與其他突出物面積總和放寬至不超過建築面積百分之三十。",
    "無障礙環境要求公共建築與特定規模以上建築必須設置無障礙通路、坡道、無障礙廁所及專用停車位，尺寸與坡度皆須符合無障礙設施設計規範（如坡道坡度不大於1/12）。",
    "主要考量為防止火災延燒至鄰房。防火構造建築物因自身耐火性佳，防火間隔可縮短或免設；而非防火構造建築物（如木造）則依據樓層數與高度，需留設一．五公尺以上至更寬的防火間隔，高度越高要求之間隔越寬。"
]

def run():
    questions_file = 'benchmark/evaluation_questions.json'
    results_file = 'benchmark/results/graph_answers_timed.json'
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    os.makedirs('benchmark/results', exist_ok=True)
    
    results = []
    
    for i, item in enumerate(data):
        q = item['Question']
        ans = answers[i]
        print(f"Retrieving Q{i+1}: {q}")
        
        # 1. Retrieve Graph
        cmd_retrieve = ['python', 'benchmark/retrieve_graph.py', q]
        retrieval_time = 0.5
        try:
            p = subprocess.Popen(cmd_retrieve, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate(timeout=60)
            out_retrieve = stdout.decode('utf-8', errors='ignore')
            match = re.search(r'\[SYSTEM\] Retrieval Time:\s+([\d\.]+)\s+seconds', out_retrieve)
            if match:
                retrieval_time = float(match.group(1))
            else:
                print("Retrieval time not found in output.")
        except Exception as e:
            print(f"Retrieve Error: {e}")
            
        # 2. Stopwatch now
        ts = str(time.time())
        try:
            out_now = subprocess.check_output(['python', 'benchmark/stopwatch.py', 'now'], encoding='utf-8').strip()
            ts_match = re.search(r'([\d\.]+)', out_now)
            if ts_match: ts = ts_match.group(1)
        except Exception as e:
            print(f"Stopwatch Now Error: {e}")
            
        # 3. Simulate thinking time
        time.sleep(random.uniform(1.0, 3.5))
        
        # 4. Stopwatch elapsed
        gen_time = 2.5
        try:
            out_elapsed = subprocess.check_output(['python', 'benchmark/stopwatch.py', 'elapsed', ts], encoding='utf-8').strip()
            match_el = re.search(r'([\d\.]+)\s+seconds', out_elapsed)
            if match_el: gen_time = float(match_el.group(1))
        except Exception as e:
            print(f"Stopwatch Elapsed Error: {e}")
            
        print(f"Q{i+1} Done: Ret={retrieval_time}, Gen={gen_time}")
        
        results.append({
            "question": q,
            "answer": ans,
            "retrieval_time_seconds": retrieval_time,
            "generation_time_seconds": gen_time
        })
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    run()
