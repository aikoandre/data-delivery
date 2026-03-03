from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Definições padrão da DAG
default_args = {
    'owner': 'engenheiro_dados',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definindo a DAG (Agendada para rodar todo dia à meia-noite)
with DAG(
    'dag_data_delivery_etl',
    default_args=default_args,
    description='Pipeline de ETL para o Data Delivery (PostgreSQL)',
    schedule_interval='0 0 * * *',
    catchup=False,
) as dag:

    # Tarefa 1: Rodar o script de ingestão (Python)
    # No mundo real, os caminhos precisariam refletir a estrutura do servidor do Airflow
    task_ingestao = BashOperator(
        task_id='ingestao_dados_raw',
        bash_command='python /caminho/do/projeto/scripts/ingestao_dados.py',
    )

    # Tarefa 2: Rodar o script de modelagem DW (Python que executa SQL)
    task_modelagem = BashOperator(
        task_id='modelagem_dw_star_schema',
        bash_command='python /caminho/do/projeto/scripts/modelagem_dw.py',
    )

    # Definindo a ordem de execução (Dependência)
    # A modelagem SÓ PODE RODAR se a ingestão der certo
    task_ingestao >> task_modelagem