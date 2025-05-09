import os
import httpx
import json
import pandas as pd
from dotenv import load_dotenv
import glob

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
# IMPORTANTE: Agora usando "numero_identificacao" em vez de "id_estudante"
DADOS_EXEMPLO = {
    1984957: {  # Número de identificação do aluno
        "nome": "LEANDRO",
        "sobrenome": "AUGUSTO ESTEVAM CRISTINA",
        "presencas": {
            "07/05/2025": "Presente",
            "08/05/2025 19:00": "Presente",
            "08/05/2025 20:00": "Presente",
            "09/05/2025 19:00": "Presente",
            "09/05/2025 20:00": "Data Futura"
        }
    },
    2165351: {  # Número de identificação do aluno
        "nome": "LUCCAS",
        "sobrenome": "ADELINO JORDÃO DA SILVA",
        "presencas": {
            "07/05/2025": "Presente",
            "08/05/2025 19:00": "Presente",
            "08/05/2025 20:00": "Presente",
            "09/05/2025 19:00": "Presente",
            "09/05/2025 20:00": "Data Futura"
        }
    },
    2029434: {  # Número de identificação do aluno
        "nome": "NICHOLAS",
        "sobrenome": "ADORNI DA SILVA",
        "presencas": {
            "07/05/2025": "Ausente",
            "08/05/2025 19:00": "Ausente",
            "08/05/2025 20:00": "Ausente",
            "09/05/2025 19:00": "Ausente",
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

# Função auxiliar para encontrar qualquer arquivo Excel no sistema
def encontrar_excel():
    """Procura por qualquer arquivo Excel no sistema"""
    caminhos_a_verificar = [
        "data/*.xlsx",       # Na pasta data/
        "*.xlsx",            # Na raiz
        "../data/*.xlsx",    # Um nível acima
        "../../data/*.xlsx", # Dois níveis acima
    ]
    
    for padrao in caminhos_a_verificar:
        arquivos = glob.glob(padrao)
        if arquivos:
            print(f"Arquivos Excel encontrados com padrão {padrao}:")
            for arquivo in arquivos:
                print(f"  - {arquivo}")
            return arquivos[0]  # Retorna o primeiro arquivo encontrado
    
    # Informações de debug
    print("Nenhum arquivo Excel encontrado. Informações de depuração:")
    print(f"Diretório atual: {os.getcwd()}")
    print("Conteúdo do diretório atual:")
    for item in os.listdir('.'):
        print(f"  - {item}")
    if os.path.exists('data'):
        print("Conteúdo do diretório 'data':")
        for item in os.listdir('data'):
            print(f"  - {item}")
    
    return None

# Função para carregar dados do Excel para o Parse Server
async def carregar_excel():
    """Carrega dados do Excel para o Parse Server"""
    # Verificar se a classe já tem dados
    try:
        count = await contar_registros()
        if count > 0:
            print(f"Já existem {count} registros no Parse Server. Pulando importação.")
            return True
    except Exception as e:
        print(f"Erro ao verificar registros existentes: {e}")
    
    # Encontrar arquivo Excel
    arquivo_excel = encontrar_excel()
    
    if arquivo_excel:
        print(f"Arquivo Excel encontrado: {arquivo_excel}")
        try:
            # Ler o arquivo Excel
            df = pd.read_excel(arquivo_excel)
            print(f"Total de registros encontrados no Excel: {len(df)}")
            print(f"Colunas encontradas: {df.columns.tolist()}")
            
            # Processar dados para o Parse Server
            registros = []
            for i, row in df.iterrows():
                try:
                    # ALTERAÇÃO: Mapear dados usando "Número de identificação" em vez de "ID do Estudante"
                    registro = {
                        "id_estudante": int(row["ID do Estudante"]),  # Mantemos para referência
                        "numero_identificacao": int(row["Número de identificação"]),  # Nova chave principal
                        "nome": str(row["Nome"]),
                        "sobrenome": str(row["Sobrenome"]),
                        "email": str(row["Endereço de email"]) if pd.notna(row["Endereço de email"]) else "",
                        "dia_07_05": int(row["7/05/2025"]) if pd.notna(row["7/05/2025"]) else 0,
                        "dia_08_05_19h": int(row["8/05/2025 19:00 "]) if pd.notna(row["8/05/2025 19:00 "]) else 0,
                        "dia_08_05_20h": int(row["8/05/2025 20:00"]) if pd.notna(row["8/05/2025 20:00"]) else 0,
                        "dia_09_05_19h": int(row["9/05/2025 19:00 "]) if pd.notna(row["9/05/2025 19:00 "]) else 0,
                        "dia_09_05_20h": int(row["9/05/2025 20:00"]) if pd.notna(row["9/05/2025 20:00"]) else 0
                    }
                    registros.append(registro)
                except Exception as e:
                    print(f"Erro ao processar registro {i}: {e}")
            
            # Inserir registros no Parse Server
            await inserir_registros(registros)
            print(f"Importação concluída! {len(registros)} registros processados.")
            return True
            
        except Exception as e:
            print(f"Erro ao processar arquivo Excel {arquivo_excel}: {e}")
    
    # Se não encontrou o arquivo ou houve erro
    print("Arquivo Excel não encontrado ou erro ao processá-lo. Usando dados de exemplo.")
    
    # Inserir dados de exemplo
    await inserir_dados_exemplo()
    return False

# Função para contar registros no Parse Server
async def contar_registros():
    """Conta quantos registros existem na classe Presenca"""
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
                print(f"Erro ao contar registros: {response.status_code} {response.text}")
                return 0
    except Exception as e:
        print(f"Erro ao contar registros: {e}")
        return 0

# Função para inserir registros no Parse Server
async def inserir_registros(registros):
    """Insere registros no Parse Server"""
    if not registros:
        print("Nenhum registro para inserir.")
        return
    
    print(f"Inserindo {len(registros)} registros no Parse Server...")
    
    async with httpx.AsyncClient() as client:
        # Inserir em lotes para não sobrecarregar a API
        batch_size = 50
        for i in range(0, len(registros), batch_size):
            batch = registros[i:i+batch_size]
            print(f"Processando lote de {len(batch)} registros...")
            
            for registro in batch:
                try:
                    response = await client.post(
                        f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                        headers=PARSE_HEADERS,
                        json=registro
                    )
                    
                    if response.status_code != 201:
                        print(f"Erro ao inserir registro: {response.status_code} {response.text}")
                except Exception as e:
                    print(f"Exceção ao inserir registro: {e}")

# Função para inserir dados de exemplo
async def inserir_dados_exemplo():
    """Insere dados de exemplo no Parse Server"""
    print("Inserindo dados de exemplo no Parse Server...")
    
    registros = []
    for numero_id, aluno in DADOS_EXEMPLO.items():
        registro = {
            "numero_identificacao": numero_id,  # ALTERAÇÃO: Usando número de identificação
            "id_estudante": 0,  # Valor padrão já que não temos o ID do estudante nos dados de exemplo
            "nome": aluno["nome"],
            "sobrenome": aluno["sobrenome"],
            "dia_07_05": 1 if aluno["presencas"]["07/05/2025"] == "Presente" else 0,
            "dia_08_05_19h": 1 if aluno["presencas"]["08/05/2025 19:00"] == "Presente" else 0,
            "dia_08_05_20h": 1 if aluno["presencas"]["08/05/2025 20:00"] == "Presente" else 0,
            "dia_09_05_19h": 1 if aluno["presencas"]["09/05/2025 19:00"] == "Presente" else 0,
            "dia_09_05_20h": 2  # Data futura
        }
        registros.append(registro)
    
    await inserir_registros(registros)
    print(f"Inseridos {len(registros)} registros de exemplo.")

# ALTERAÇÃO: Função para buscar um aluno pelo número de identificação
async def buscar_aluno(numero_id):
    try:
        # Construir a consulta no formato do Parse Server usando número de identificação
        where = {"numero_identificacao": numero_id}
        
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
                        "09/05/2025 19:00": STATUS_MAP[aluno.get("dia_09_05_19h", 0)],
                        "09/05/2025 20:00": STATUS_MAP[aluno.get("dia_09_05_20h", 2)]
                    }
                    
                    return {
                        "nome": aluno.get("nome", ""),
                        "sobrenome": aluno.get("sobrenome", ""),
                        "presencas": presencas
                    }
                
            # Se não encontrar ou houver erro, verificar nos dados de exemplo
            if numero_id in DADOS_EXEMPLO:
                print(f"Aluno com número de identificação {numero_id} encontrado nos dados de exemplo.")
                return DADOS_EXEMPLO[numero_id]
                
            return None
                
    except Exception as e:
        print(f"Erro ao buscar aluno: {e}")
        
        # Em caso de erro, tentar buscar nos dados de exemplo
        if numero_id in DADOS_EXEMPLO:
            print(f"Aluno com número de identificação {numero_id} encontrado nos dados de exemplo (após erro).")
            return DADOS_EXEMPLO[numero_id]
            
        return None
