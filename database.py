import os
import httpx
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Parse Server
PARSE_APP_ID = os.environ.get("PARSE_APP_ID", "qCcHm3fS1PDaQkakoP3KUwyKrVjEKVGUQwoZPWHQ")
PARSE_REST_API_KEY = os.environ.get("PARSE_REST_API_KEY", "asaHz9ma1fRBTzEaU2w6ErHZBTEh5iYwvn1tgNJ1")
PARSE_SERVER_URL = os.environ.get("PARSE_SERVER_URL", "https://parseapi.back4app.com")

# Headers para requisições ao Parse Server
PARSE_HEADERS = {
    "X-Parse-Application-Id": PARSE_APP_ID,
    "X-Parse-REST-API-Key": PARSE_REST_API_KEY,
    "Content-Type": "application/json"
}

# Nome da classe no Parse Server
PRESENCA_CLASS = "Presenca"

# Função para testar a conexão com o Parse Server
async def test_connection():
    """Função para testar a conexão com o Parse Server"""
    try:
        async with httpx.AsyncClient() as client:
            # Tentar listar as classes
            response = await client.get(
                f"{PARSE_SERVER_URL}/schemas", 
                headers=PARSE_HEADERS
            )
            
            if response.status_code == 200:
                return {
                    "message": "Conexão com Parse Server bem-sucedida",
                    "schemas": response.json(),
                    "config": {
                        "PARSE_SERVER_URL": PARSE_SERVER_URL,
                        "PARSE_APP_ID": PARSE_APP_ID[:5] + "..." if PARSE_APP_ID else None,
                        "PARSE_CLASS": PRESENCA_CLASS
                    }
                }
            else:
                return {
                    "message": f"Erro ao conectar: {response.status_code}",
                    "response": response.text
                }
    except Exception as e:
        return {"error": str(e)}

# Função para inicializar o banco de dados
async def init_db():
    try:
        # Verificar a conexão com o Parse Server
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                headers=PARSE_HEADERS,
                params={"limit": 1}
            )
            
            if response.status_code == 200:
                print("Conexão com Parse Server estabelecida com sucesso!")
            else:
                print(f"Erro ao conectar ao Parse Server: {response.status_code} {response.text}")
        
    except Exception as e:
        print(f"Erro ao conectar ao Parse Server: {e}")
        raise

# Função para contar documentos
async def count_documents():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                headers=PARSE_HEADERS,
                params={"count": 1, "limit": 0}
            )
            
            if response.status_code == 200:
                return response.json().get("count", 0)
            else:
                print(f"Erro ao contar documentos: {response.status_code} {response.text}")
                return 0
                
    except Exception as e:
        print(f"Erro ao contar documentos: {e}")
        return 0

# Função para inserir múltiplos documentos
async def insert_many(documents):
    try:
        # O Parse Server não tem um endpoint de inserção em massa
        # Inserimos um por um em uma sessão do cliente HTTP
        async with httpx.AsyncClient() as client:
            for document in documents:
                response = await client.post(
                    f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                    headers=PARSE_HEADERS,
                    json=document
                )
                
                if response.status_code != 201:
                    print(f"Erro ao inserir documento: {response.status_code} {response.text}")
            
        print(f"{len(documents)} registros inseridos no Parse Server.")
            
    except Exception as e:
        print(f"Erro ao inserir documentos: {e}")
        raise

# Função para encontrar um documento
async def find_one(query):
    try:
        # Construir a consulta no formato do Parse Server
        where = {}
        for key, value in query.items():
            where[key] = value
            
        params = {
            "where": json.dumps(where),
            "limit": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                headers=PARSE_HEADERS,
                params=params
            )
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0]
                return None
            else:
                print(f"Erro ao buscar documento: {response.status_code} {response.text}")
                return None
                
    except Exception as e:
        print(f"Erro ao buscar documento: {e}")
        return None

# Função para criar um índice (não usado no Parse Server, mas mantido para compatibilidade)
async def create_index(field_name):
    # Parse Server gerencia índices automaticamente
    pass

# Mapeamento das funções para manter compatibilidade com o código original
presenca_collection = type('DummyCollection', (), {
    'count_documents': count_documents,
    'insert_many': insert_many,
    'find_one': find_one,
    'create_index': create_index
})()
