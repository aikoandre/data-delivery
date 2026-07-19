import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_task(script_path):
    logging.info(f"Iniciando a tarefa: {script_path}")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        logging.info(f"Tarefa {script_path} concluída com sucesso.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Falha na tarefa {script_path}. Erro: {e}")
        sys.exit(1)

def main():
    logging.info("Iniciando o DAG simples de ETL (Data Delivery)...")
    
    # Definindo a ordem do DAG
    tasks = [
        "scripts/ingestao_dados.py",
        "scripts/modelagem_dw.py"
    ]
    
    for task in tasks:
        run_task(task)
        
    logging.info("Pipeline finalizado com sucesso!")

if __name__ == "__main__":
    main()