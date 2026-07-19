import pandas as pd
import json
from sqlalchemy import create_engine
import os

from dotenv import load_dotenv
load_dotenv()

# 1. Configuração da Conexão com o Banco de Dados (PostgreSQL via Docker)
# Formato: dialect+driver://username:password@host:port/database
DATABASE_URI = os.getenv('DB_URL', 'postgresql+psycopg2://usuario_etl:senha_super_secreta@localhost:5433/data_delivery')
engine = create_engine(DATABASE_URI)

print("Iniciando processo de ETL...")

# 2. EXTRAÇÃO (Extract) - Lendo os dados brutos
print("Extraindo dados...")
caminho_raw = '../data/raw/'

df_restaurantes = pd.read_csv(os.path.join(caminho_raw, 'restaurantes.csv'))
df_pedidos = pd.read_csv(os.path.join(caminho_raw, 'pedidos.csv'))

with open(os.path.join(caminho_raw, 'usuarios.json'), 'r', encoding='utf-8') as f:
    dados_usuarios = json.load(f)
df_usuarios = pd.DataFrame(dados_usuarios)


# 3. TRANSFORMAÇÃO (Transform) - Limpeza e Qualidade de Dados
print("Transformando e limpando os dados...")

# Limpeza na tabela de Pedidos:
tamanho_original = len(df_pedidos)

# a) Remover linhas onde o valor_total é nulo (NaN)
df_pedidos = df_pedidos.dropna(subset=['valor_total'])

# b) Remover linhas onde o valor_total é negativo ou zero
df_pedidos = df_pedidos[df_pedidos['valor_total'] > 0]

# c) Garantir que as datas estão no formato correto (datetime)
df_pedidos['data_pedido'] = pd.to_datetime(df_pedidos['data_pedido'])
df_usuarios['data_cadastro'] = pd.to_datetime(df_usuarios['data_cadastro'])

linhas_removidas = tamanho_original - len(df_pedidos)
print(f"  - Limpeza concluída: {linhas_removidas} pedidos inválidos foram removidos.")


# 4. CARGA (Load) - Inserindo no Banco de Dados (Camada Raw)
print("Carregando dados no banco (PostgreSQL)...")

# O parâmetro if_exists='replace' recria a tabela se ela já existir. 
# Em produção, usaríamos 'append' (adicionar) e criaríamos um controle de chaves.
# O schema='public' é o esquema padrão do Postgres.
df_restaurantes.to_sql('raw_restaurantes', engine, schema='public', if_exists='replace', index=False)
print("  - Tabela raw_restaurantes carregada.")

df_usuarios.to_sql('raw_usuarios', engine, schema='public', if_exists='replace', index=False)
print("  - Tabela raw_usuarios carregada.")

df_pedidos.to_sql('raw_pedidos', engine, schema='public', if_exists='replace', index=False)
print("  - Tabela raw_pedidos carregada.")

print("\nProcesso ETL finalizado com sucesso!")