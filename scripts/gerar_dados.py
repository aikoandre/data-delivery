import pandas as pd
import random
from datetime import datetime, timedelta
import json
import os
import numpy as np

# Garante que a pasta de destino existe
os.makedirs('../data/raw', exist_ok=True)

print("Iniciando a geração de dados...")

# 1. Gerando Restaurantes (CSV)
restaurantes = {
    'id_restaurante': range(1, 11),
    'nome': ['Pizza Planet', 'Burger King', 'Sushi da Esquina', 'Taco Loco', 'Vegan Deli', 
             'Churrascaria Fogo', 'Massa Nostra', 'Saladinha', 'Padaria Central', 'Frango Frito'],
    'tipo_culinaria': ['Pizza', 'Hamburguer', 'Japonesa', 'Mexicana', 'Vegana', 
                       'Carnes', 'Italiana', 'Saudável', 'Padaria', 'Fast Food']
}
df_restaurantes = pd.DataFrame(restaurantes)
df_restaurantes.to_csv('../data/raw/restaurantes.csv', index=False)
print("- restaurantes.csv gerado com sucesso!")

# 2. Gerando Usuários (JSON)
nomes = ['Ana', 'Bruno', 'Carlos', 'Daniela', 'Eduardo', 'Fernanda', 'Gabriel', 'Helena', 'Igor', 'Juliana']
sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues']
estados = ['SP', 'RJ', 'MG', 'PR', 'SC', 'RS', 'BA']

usuarios = []
for i in range(1, 51): # 50 usuários
    data_cadastro = datetime.now() - timedelta(days=random.randint(10, 365))
    usuarios.append({
        'id_usuario': i,
        'nome': f"{random.choice(nomes)} {random.choice(sobrenomes)}",
        'estado': random.choice(estados),
        'data_cadastro': data_cadastro.strftime('%Y-%m-%d %H:%M:%S')
    })

with open('../data/raw/usuarios.json', 'w', encoding='utf-8') as f:
    json.dump(usuarios, f, ensure_ascii=False, indent=4)
print("- usuarios.json gerado com sucesso!")

# 3. Gerando Pedidos (CSV) - Com dados sujos de propósito!
pedidos = []
status_list = ['Entregue', 'Cancelado', 'Em Rota']

for i in range(1, 1001): # 1000 pedidos
    data_pedido = datetime.now() - timedelta(days=random.randint(0, 60))
    
    # Gerando o valor (alguns serão nulos ou negativos para simular erros)
    chance_erro = random.random()
    if chance_erro < 0.05: # 5% de chance de ser negativo
        valor = round(random.uniform(-50.0, -5.0), 2)
    elif chance_erro > 0.95: # 5% de chance de ser nulo (NaN)
        valor = np.nan
    else:
        valor = round(random.uniform(15.0, 150.0), 2)

    pedidos.append({
        'id_pedido': i,
        'id_usuario': random.randint(1, 50),
        'id_restaurante': random.randint(1, 10),
        'data_pedido': data_pedido.strftime('%Y-%m-%d %H:%M:%S'),
        'valor_total': valor,
        'status': random.choice(status_list)
    })

df_pedidos = pd.DataFrame(pedidos)
df_pedidos.to_csv('../data/raw/pedidos.csv', index=False)
print("- pedidos.csv gerado com sucesso!")
print("\nGeracao concluida! Verifique a pasta 'data/raw'.")