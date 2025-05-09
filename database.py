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

# Dados em memória para backup (caso o Parse Server não esteja disponível)
DADOS_EXEMPLO = {
    12345: {
        "nome": "ESTUDANTE",
        "sobrenome": "TESTE",
        "presencas": {
            "07/05/2025": "Presente",
            "08/05/2025 19:00": "Presente",
            "08/05/2025 20:00": "Presente",
            "09/05/2025 19:00": "Data Futura",
            "09/05/2025 20:00": "Data Futura"
        }
    },
    54321: {
        "nome": "ALUNO",
        "sobrenome": "EXEMPLO",
        "presencas": {
            "07/05/2025": "Ausente",
            "08/05/2025 19:00": "Ausente",
            "08/05/2025 20:00": "Ausente",
            "09/05/2025 19:00": "Data Futura",
            "09/05/2025 20:00": "Data Futura"
        }
    }
}

# Mapeamento de status
STATUS_MAP = {
    0: "Ausente",
    1: "Presente",
    2: "Data Futura"
}

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
                return True
            else:
                print(f"Erro ao conectar ao Parse Server: {response.status_code} {response.text}")
                return False
        
    except Exception as e:
        print(f"Erro ao conectar ao Parse Server: {e}")
        return False

# Função para verificar se a classe Presenca existe ou criar se não existir
async def ensure_presenca_class():
    try:
        # Primeiro, verificar se a classe já existe
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PARSE_SERVER_URL}/schemas/{PRESENCA_CLASS}",
                headers=PARSE_HEADERS
            )
            
            # Se a classe não existir, criar com alguns dados de exemplo
            if response.status_code == 404:
                print(f"Classe {PRESENCA_CLASS} não encontrada. Criando com dados de exemplo...")
                
                # Inserir dados de exemplo
                for id_estudante, aluno in DADOS_EXEMPLO.items():
                    # Converter para o formato correto do Parse Server
                    document = {
                        "id_estudante": id_estudante,
                        "nome": aluno["nome"],
                        "sobrenome": aluno["sobrenome"],
                        "dia_07_05": 1 if aluno["presencas"]["07/05/2025"] == "Presente" else 0,
                        "dia_08_05_19h": 1 if aluno["presencas"]["08/05/2025 19:00"] == "Presente" else 0,
                        "dia_08_05_20h": 1 if aluno["presencas"]["08/05/2025 20:00"] == "Presente" else 0,
                        "dia_09_05_19h": 2,  # Data futura
                        "dia_09_05_20h": 2   # Data futura
                    }
                    
                    # Inserir no Parse Server
                    create_response = await client.post(
                        f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                        headers=PARSE_HEADERS,
                        json=document
                    )
                    
                    if create_response.status_code == 201:
                        print(f"Registro para ID {id_estudante} criado com sucesso!")
                    else:
                        print(f"Erro ao criar registro: {create_response.status_code} {create_response.text}")
            else:
                print(f"Classe {PRESENCA_CLASS} já existe no Parse Server.")
                
    except Exception as e:
        print(f"Erro ao verificar ou criar classe: {e}")

# Função para buscar um aluno pelo ID
async def buscar_aluno(id_estudante):
    try:
        # Construir a consulta no formato do Parse Server
        where = {"id_estudante": id_estudante}
        
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
                    # Formatar o resultado no formato esperado
                    aluno = results[0]
                    presencas = {
                        "07/05/2025": STATUS_MAP[aluno.get("dia_07_05", 0)],
                        "08/05/2025 19:00": STATUS_MAP[aluno.get("dia_08_05_19h", 0)],
                        "08/05/2025 20:00": STATUS_MAP[aluno.get("dia_08_05_20h", 0)],
                        "09/05/2025 19:00": STATUS_MAP[aluno.get("dia_09_05_19h", 2)],
                        "09/05/2025 20:00": STATUS_MAP[aluno.get("dia_09_05_20h", 2)]
                    }
                    
                    return {
                        "nome": aluno.get("nome", ""),
                        "sobrenome": aluno.get("sobrenome", ""),
                        "presencas": presencas
                    }
                
            # Se não encontrar ou houver erro, verificar nos dados de exemplo
            if id_estudante in DADOS_EXEMPLO:
                print(f"Aluno {id_estudante} encontrado nos dados de exemplo.")
                return DADOS_EXEMPLO[id_estudante]
                
            return None
                
    except Exception as e:
        print(f"Erro ao buscar aluno: {e}")
        
        # Em caso de erro, tentar buscar nos dados de exemplo
        if id_estudante in DADOS_EXEMPLO:
            print(f"Aluno {id_estudante} encontrado nos dados de exemplo (após erro).")
            return DADOS_EXEMPLO[id_estudante]
            
        return None
