import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import time

load_dotenv()

id_loja_aloha = 234402
id_loja_fabrica = 399776

access_token = os.getenv('ACCESS_TOKEN')
secret_access_token = os.getenv('SECRET_ACCESS_TOKEN')
token = os.getenv('TOKEN')

headers = {
    'access-token': access_token,
    'secret-access-token': secret_access_token
}

headers_system = {
    'token': token,
}

def realizar_operacoes():

    #? Puxa os produtos da loja Aloha
    response = requests.get(f'https://api.beteltecnologia.com/produtos?grupo_id=2571246&loja_id={id_loja_aloha}', headers=headers)

    response = response.json()
    response = response['data']


    produtos = []
    total_pedido = 0
    for produto in response:

        if produto['estoque'] >= 0:
            continue
        
        produtos.append({
            'produto_id': produto['id'],
            'nome_produto': produto['nome'],
            'quantidade': abs(produto['estoque']),
            'valor_custo': 14,
        })
        total_pedido += abs(produto['estoque']) * 14

    if total_pedido == 0:
        return


    data_atual = datetime.now()
    data_formatada = data_atual.strftime('%Y-%m-%d')

    json = {
        'fornecedor_id': 2854662, # Fabrica
        'situacao_id': 881445, # Confirmado
        'loja_id': id_loja_aloha,
        'data_emissao': data_formatada,
        'produtos': produtos,
        'condicao_pagamento': 'a_vista',
        'forma_pagamento_id': 2219799, # Pix
        'numero_parcelas': 1,
        "pagamentos": [
            {
                "pagamento": {
                    "data_vencimento": data_formatada,
                    "valor": total_pedido,
                    "forma_pagamento_id": 2219799, # Pix
                }
            },
        ],
    }

    #? Faz a compra da loja Aloha
    response = requests.post('https://api.beteltecnologia.com/compras', json=json, headers=headers)

    #? Puxa os produtos da loja Fabrica
    response = requests.get(f'https://api.beteltecnologia.com/produtos?grupo_id=4208778&loja_id={id_loja_fabrica}', headers=headers)

    response = response.json()
    response = response['data']

    venda = []
    for produto_fabrica in response:

        for produto_aloha in produtos:
            if produto_fabrica['nome'] == produto_aloha['nome_produto']:
                venda.append({
                    'produto_id': produto_fabrica['id'],
                    'quantidade': produto_aloha['quantidade'],
                    'valor_venda': 14,
                })


    json = {
        'tipo': 'produto',
        'cliente_id': 35312609, # Aloha
        'situacao_id': 3395254, # Concluída
        'loja_id': id_loja_fabrica,
        'data': data_formatada,
        'prazo_entrega': data_formatada,
        'produtos': venda,
        "pagamentos": [
            {
                "pagamento": {
                    "data_vencimento": data_formatada,
                    "valor": total_pedido,
                    "forma_pagamento_id": 4418087, # Cora (Gelo & Sabor)
                }
            },
        ],
    }

    #? Faz a venda da loja Fabrica
    response = requests.post('https://api.beteltecnologia.com/vendas', json=json, headers=headers)

    #? Sincroniza o System
    response = requests.get('https://www.alohasystem.com.br/api/pacotes/integration/sync', headers=headers)

    data_atual = datetime.now()
    data_atual = data_atual.strftime('%d/%m/%Y %H:%M:%S')
    print(f'Compra realizada com sucesso! {data_atual}')

while True:
    realizar_operacoes()
    time.sleep(60)