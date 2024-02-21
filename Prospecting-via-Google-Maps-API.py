import requests
import json
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# Configurações das integrações 
url_trello = "url_trello"
id_lista_trello = "id_lista_trello"
API_Key_trello =  "API_Key_trello"
API_Token_trello = "API_Token_trello"
chave_api = "chave_api"

def buscar_lojas(latitude, longitude, raio, chave_api):
    
    ##Esta função realiza uma solicitação à API do Google Places para buscar lojas de diferentes segmentos para prospecção de vendas.
    
    db = []
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    parametros = {
        "location": f"{latitude},{longitude}",
        "radius": raio,
        "type": "clothing_store",
        "key": chave_api
    }
    resposta = requests.get(url, params=parametros)
    dados = resposta.json()
    if dados["status"] == "OK":
        for loja in dados["results"]:
            
            nome_loja = loja["name"]
            local_loja = loja['vicinity']
            # Acessar a API detalhada para obter mais informações sobre a loja, incluindo o número de telefone
            detalhes_loja = obter_detalhes_loja(loja["place_id"], chave_api)
            telefone = detalhes_loja.get("formatted_phone_number", None)
            if telefone is not None:
                print(f"Nome da loja: {nome_loja}, Telefone: {telefone}")
                db.append({'Nome': nome_loja, "Telefone": telefone, "Endereço": local_loja})
             
                 

    else:
        print("Caiu aqui")
        longitude = random.uniform(-38.373133259744975, -38.663548188499256)
        latitude = random.uniform(-3.694437528842489, -3.8988945425378194)
        dados=buscar_lojas(latitude, longitude, raio, chave_api)
        
        return dados
    

    return db

def obter_detalhes_loja(place_id, chave_api): ## retorna os as informações chaves do local.
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    parametros = {
        "place_id": place_id,
        "key": chave_api
    }
    resposta = requests.get(url, params=parametros)
    dados = resposta.json()
    
    return dados["result"]

def Enviar_MongoDB_Atlas(dados):
    uri = f"mongodb+srv://thales:admin@cluster-pipeline.8znkxsj.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client['Leads']
    collection = db['Leads_Trello']

    collection.insert_many(dados)

# Coordenadas aleatórias dentro de uma demilitada de Fortaleza-CE e Regioes metropolitanas.

longitude = random.uniform(-38.373133259744975, -38.663548188499256)
latitude = random.uniform(-3.694437528842489, -3.8988945425378194)
raio = 500  # 500 metros


# Chamada para buscar lojas com as informações necessárias para prospecção a
dados = buscar_lojas(latitude, longitude, raio, chave_api)




# Criando cartões no Trello para cada loja encontrada para facilitar a venda
for lead_data in dados:
    headers = {"Accept": "application/json"}
    query = {
        'address': lead_data.get('Endereço', ''),
        'name': f"{lead_data.get('Nome','')} - {lead_data.get('Telefone', '')}",
        'idList': id_lista_trello,
        'key': API_Key_trello,
        'token': API_Token_trello
    }

    
    response = requests.post(url_trello, headers=headers, params=query)

    if response.status_code == 200:
        print(f"Cartão para '{lead_data['Nome']}' criado com sucesso!")
    else:
        print(f"Erro ao criar o cartão para '{lead_data['Nome']}'. Código de status: {response.status_code}")
        print(response.text)
    



Enviar_MongoDB_Atlas(dados)