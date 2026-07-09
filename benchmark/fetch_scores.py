import os
from langsmith import Client

from dotenv import load_dotenv

def main():
    load_dotenv()
    client = Client()
    dataset_name = "Taiwan_Building_Code_Benchmark_V3"
    projects = list(client.list_projects(reference_dataset_name=dataset_name))
    
    # 取最新的 3 個 Project (因為我們剛剛跑了 Hybrid, Graph, OKF)
    projects.sort(key=lambda p: p.start_time, reverse=True)
    latest_projects = projects[:3]
    
    print("=== LangSmith 評分結果 ===")
    results = []
    for p in latest_projects:
        print(f"Project: {p.name}")
        try:
            # Read project to get populated feedback stats
            proj = client.read_project(project_name=p.name)
            if hasattr(proj, 'feedback_stats') and proj.feedback_stats:
                # feedback_stats is usually a dict like {'Correctness': {'avg': 0.8}}
                for key, val in proj.feedback_stats.items():
                    print(f"  {key}: {val.get('avg', 0):.2f}")
            else:
                runs = list(client.list_runs(project_name=p.name, is_root=True))
                scores = []
                for r in runs:
                    feedbacks = list(client.list_feedback(run_ids=[r.id]))
                    for f in feedbacks:
                        if f.key and f.key.lower() == "correctness" and f.score is not None:
                            scores.append(f.score)
                if scores:
                    print(f"  Correctness (Avg): {sum(scores)/len(scores):.2f}")
                else:
                    print("  No feedback found.")
        except Exception as e:
            print(f"Error fetching stats: {e}")
        
if __name__ == "__main__":
    main()
