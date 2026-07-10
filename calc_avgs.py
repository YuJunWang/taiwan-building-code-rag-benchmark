import json
import statistics

def load_data(file_name):
    with open(f'benchmark/results/{file_name}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    else:
        return data.get('results', [])

hybrid = load_data('hybrid_answers_timed.json')
graph = load_data('graph_answers_timed.json')
okf = load_data('okf_agent_answers_timed.json')

def get_avgs(data):
    retrievals = [float(x['retrieval_time_seconds']) for x in data if 'retrieval_time_seconds' in x]
    generations = [float(x['generation_time_seconds']) for x in data if 'generation_time_seconds' in x]
    return statistics.mean(retrievals) if retrievals else 0, statistics.mean(generations) if generations else 0

h_r, h_g = get_avgs(hybrid)
g_r, g_g = get_avgs(graph)
o_r, o_g = get_avgs(okf)

print(f"Hybrid: R={h_r:.2f}s, G={h_g:.2f}s")
print(f"Graph: R={g_r:.2f}s, G={g_g:.2f}s")
print(f"OKF: R={o_r:.2f}s, G={o_g:.2f}s")
