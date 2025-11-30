import pandas as pd
import os
import sys

# --- Ferramentas de Avaliação ---
try:
    # 1. ROUGE Clássico (Lexical)
    from rouge_score import rouge_scorer

    print("Biblioteca 'rouge_score' (Clássica) carregada.")
except ImportError:
    print("ERRO: 'rouge_score' não encontrada. Instale com: pip install rouge-score")
    rouge_scorer = None

try:
    # 2. BERTScore (Semântico) - A sua "ROUGE-SS"
    from bert_score import score as bert_scorer

    print("Biblioteca 'bert_score' (Semântica) carregada.")
except ImportError:
    print("ERRO: 'bert_score' não encontrada. Instale com: pip install bert-score torch")
    bert_scorer = None


def calculate_all_scores_from_files():
    if not rouge_scorer or not bert_scorer:
        return

    # --- Configuração ---
    BASE_DIR = "src/assets/"
    REFERENCE_FILES = {
        "after": os.path.join(BASE_DIR, "after_llm_release_comments.csv"),
        "before": os.path.join(BASE_DIR, "before_llm_release.csv")
    }
    REFERENCE_COLUMN_NAME = "response"

    GENERATED_DIR = os.path.join(BASE_DIR, "generated_comments")
    GENERATED_FILES_NAMES = [
        "after_llm_release_comments_generated_responses_persona_1_few_shot.csv",
        "after_llm_release_comments_generated_responses_persona_1_zero_shot.csv",
        "after_llm_release_comments_generated_responses_persona_2_few_shot.csv",
        "after_llm_release_comments_generated_responses_persona_2_zero_shot.csv",
        "before_llm_comments_generated_responses_persona_1_few_shot.csv",
        "before_llm_comments_generated_responses_persona_1_zero_shot.csv",
        "before_llm_comments_generated_responses_persona_2_few_shot.csv",
        "before_llm_comments_generated_responses_persona_2_zero_shot.csv"
    ]
    GENERATED_FILES = [os.path.join(GENERATED_DIR, f) for f in GENERATED_FILES_NAMES]

    # O Arquivo final que conterá TODAS as métricas
    OUTPUT_FILENAME = "all_metrics_ROUGE_and_BERTScore.csv"
    # --- Fim da Configuração ---

    all_scores = []

    # Inicializa o Scorer Clássico
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=False)
        print("RougeScorer (léxico) inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar RougeScorer: {e}")
        return

    # Carregar referências
    try:
        try:
            df_ref_after = pd.read_csv(REFERENCE_FILES["after"])
            df_ref_before = pd.read_csv(REFERENCE_FILES["before"])
        except UnicodeDecodeError:
            print("UnicodeDecodeError. Tentando com 'latin-1'...")
            df_ref_after = pd.read_csv(REFERENCE_FILES["after"], encoding='latin-1')
            df_ref_before = pd.read_csv(REFERENCE_FILES["before"], encoding='latin-1')
        print("Arquivos de referência carregados.")
    except FileNotFoundError as e:
        print(f"ERRO CRÍTICO: Arquivo de referência não encontrado: {e}", file=sys.stderr)
        return

    # Loop principal
    for file_path in GENERATED_FILES:
        file_name_only = os.path.basename(file_path)
        if not os.path.exists(file_path):
            print(f"AVISO: Arquivo '{file_path}' não encontrado. Pulando.")
            continue

        print(f"\nProcessando arquivo: {file_name_only}...")

        try:
            try:
                df_gen = pd.read_csv(file_path)
            except UnicodeDecodeError:
                df_gen = pd.read_csv(file_path, encoding='latin-1')

            if "after_llm" in file_name_only:
                df_ref = df_ref_after
            elif "before_llm" in file_name_only:
                df_ref = df_ref_before
            else:
                continue

            len_gen = len(df_gen)
            len_ref = len(df_ref)
            min_len = min(len_gen, len_ref)

            if len_gen != len_ref:
                print(f"  AVISO: Incompatibilidade de linhas: {len_gen} vs {len_ref}. Processando {min_len} linhas.")

            persona = "1" if "persona_1" in file_name_only else "2"
            shot_type = "few_shot" if "few_shot" in file_name_only else "zero_shot"
            release = "after_llm" if "after_llm" in file_name_only else "before_llm"

            try:
                current_candidate_cols = {
                    'Gpt4': [col for col in df_gen.columns if
                             'Gpt4 Generated Response' in col and 'processing time' not in col][0],
                    'Gemini': [col for col in df_gen.columns if
                               'Gemini Generated Response' in col and 'processing time' not in col][0],
                    'Llama3': [col for col in df_gen.columns if
                               'Llama3 Generated Response' in col and 'processing time' not in col][0]
                }
            except IndexError:
                print(f"ERRO: Colunas das LLMs não encontradas para {file_name_only}.", file=sys.stderr)
                continue

            for index in range(min_len):
                reference_text = str(df_ref.loc[index, REFERENCE_COLUMN_NAME])
                row_gen = df_gen.iloc[index]

                if pd.isna(reference_text) or not reference_text.strip():
                    continue

                for llm_name, col_name in current_candidate_cols.items():
                    candidate_text = str(row_gen[col_name])

                    # Inicializa scores
                    rouge1_f1 = rouge2_f1 = rougeL_f1 = 0.0
                    bert_precision = bert_recall = bert_f1 = 0.0

                    if not pd.isna(candidate_text) and candidate_text.strip():

                        # 1. CALCULAR ROUGE CLÁSSICO
                        try:
                            scores_obj = scorer.score(reference_text, candidate_text)
                            rouge1_f1 = scores_obj['rouge1'].fmeasure
                            rouge2_f1 = scores_obj['rouge2'].fmeasure
                            rougeL_f1 = scores_obj['rougeL'].fmeasure
                        except Exception as e:
                            print(f"  Erro ROUGE (linha {index}, {llm_name}): {e}", file=sys.stderr)

                        # 2. CALCULAR BERTSCORE (Semântico)
                        try:
                            # lang="pt" é crucial!
                            P, R, F1 = bert_scorer(
                                [candidate_text],
                                [reference_text],
                                lang="pt",
                                verbose=False
                            )
                            # .item() extrai o valor numérico do tensor
                            bert_precision = P.item()
                            bert_recall = R.item()
                            bert_f1 = F1.item()
                        except Exception as e:
                            print(f"  Erro BERTScore (linha {index}, {llm_name}): {e}", file=sys.stderr)

                    # Salva todos os resultados
                    result = {
                        "file_name": file_name_only,
                        "release": release,
                        "persona": persona,
                        "shot_type": shot_type,
                        "row_index": index,
                        "llm": llm_name,
                        # Métricas Lexical (Baseline)
                        "rouge1_f1": rouge1_f1,
                        "rouge2_f1": rouge2_f1,
                        "rougeL_f1": rougeL_f1,
                        # Métricas Semânticas (Principal)
                        "bert_precision": bert_precision,
                        "bert_recall": bert_recall,
                        "bert_f1": bert_f1
                    }
                    all_scores.append(result)

        except Exception as e:
            print(f"Erro fatal ao processar o arquivo {file_name_only}: {e}", file=sys.stderr)

    if not all_scores:
        print("\nNenhuma pontuação calculada.", file=sys.stderr)
        return

    # Salva o DataFrame final
    df_results = pd.DataFrame(all_scores)
    df_results.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')

    print("\n--- AVALIAÇÃO COMPLETA CONCLUÍDA ---")
    print(f"Arquivo final salvo em: {OUTPUT_FILENAME}")
    print("\nAmostra dos resultados:")
    print(df_results.head())
    print(f"\nTotal de {len(all_scores)} linhas processadas.")


# --- Execução ---
if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("Iniciando cálculo da Tríade de Avaliação (ROUGE + BERTScore)...")
    calculate_all_scores_from_files()