from sqlalchemy import create_engine, text

import os
from dotenv import load_dotenv
load_dotenv()

# Conectando no banco (Agora na porta 5433!)
DATABASE_URI = os.getenv('DB_URL', 'postgresql+psycopg2://usuario_etl:senha_super_secreta@localhost:5433/data_delivery')
engine = create_engine(DATABASE_URI)

# Vamos rodar várias queries SQL. Usamos text() no SQLAlchemy para isso.
queries_modelagem = [
    # 1. Cria o schema do Data Warehouse (se não existir)
    "CREATE SCHEMA IF NOT EXISTS dw;",

    # 2. Drop nas tabelas do DW caso a gente queira rodar o script de novo do zero
    "DROP TABLE IF EXISTS dw.fato_pedidos;",
    "DROP TABLE IF EXISTS dw.dim_restaurantes;",
    "DROP TABLE IF EXISTS dw.dim_usuarios;",
    "DROP TABLE IF EXISTS dw.dim_tempo;",

    # 3. Criando a Dimensão Restaurantes
    """
    CREATE TABLE dw.dim_restaurantes AS
    SELECT 
        id_restaurante AS restaurante_id,
        nome AS restaurante_nome,
        tipo_culinaria
    FROM public.raw_restaurantes;
    """,
    "ALTER TABLE dw.dim_restaurantes ADD PRIMARY KEY (restaurante_id);",

    # 4. Criando a Dimensão Usuários
    """
    CREATE TABLE dw.dim_usuarios AS
    SELECT 
        id_usuario AS usuario_id,
        nome AS usuario_nome,
        estado AS usuario_estado,
        data_cadastro::DATE AS data_cadastro
    FROM public.raw_usuarios;
    """,
    "ALTER TABLE dw.dim_usuarios ADD PRIMARY KEY (usuario_id);",

    # 5. Criando a Dimensão Tempo
    # Extraímos os componentes de data para facilitar as análises (Mês, Ano, Dia da Semana)
    """
    CREATE TABLE dw.dim_tempo AS
    SELECT DISTINCT
        data_pedido::DATE AS tempo_id, -- A data em si será a chave
        EXTRACT(YEAR FROM data_pedido) AS ano,
        EXTRACT(MONTH FROM data_pedido) AS mes,
        EXTRACT(DAY FROM data_pedido) AS dia,
        TO_CHAR(data_pedido, 'Day') AS dia_semana -- Ex: 'Monday'
    FROM public.raw_pedidos;
    """,
    "ALTER TABLE dw.dim_tempo ADD PRIMARY KEY (tempo_id);",

    # 6. Criando a Tabela Fato
    # A Tabela Fato conecta todas as dimensões e guarda a métrica de negócio (valor_total)
    """
    CREATE TABLE dw.fato_pedidos AS
    SELECT
        p.id_pedido AS pedido_id,
        p.id_usuario AS usuario_id,
        p.id_restaurante AS restaurante_id,
        p.data_pedido::DATE AS tempo_id,
        p.valor_total,
        p.status
    FROM public.raw_pedidos p;
    """,
    "ALTER TABLE dw.fato_pedidos ADD PRIMARY KEY (pedido_id);",

    # Adicionando chaves estrangeiras na Fato (Boas práticas de modelagem)
    "ALTER TABLE dw.fato_pedidos ADD CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES dw.dim_usuarios (usuario_id);",
    "ALTER TABLE dw.fato_pedidos ADD CONSTRAINT fk_restaurante FOREIGN KEY (restaurante_id) REFERENCES dw.dim_restaurantes (restaurante_id);",
    "ALTER TABLE dw.fato_pedidos ADD CONSTRAINT fk_tempo FOREIGN KEY (tempo_id) REFERENCES dw.dim_tempo (tempo_id);"
]

print("Iniciando a modelagem do Data Warehouse (Star Schema)...")

# Executando as queries
with engine.begin() as conexao:
    for query in queries_modelagem:
        try:
            conexao.execute(text(query))
        except Exception as e:
            print(f"Erro ao executar a query: {query}")
            print(e)

print("Modelagem concluída! Tabelas dw.dim_* e dw.fato_pedidos criadas com sucesso.")