from src.execute import execute_agents
# from src.metrics.rouge import calculate_rouge_from_files
import sys
from src.metrics.rouge import calculate_all_scores_from_files
if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    calculate_all_scores_from_files()