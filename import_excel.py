import asyncio
import httpx
import json
import os
import pandas as pd
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

# Função para carregar dados do Excel e enviar para o Parse Server
async def importar_excel(arquivo_excel):
    """Importa dados de um arquivo Excel para o Parse Server"""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(arquivo_excel):
            print(f"ERRO: Arquivo Excel não encontrado: {arquivo_excel}")
            return False
        
        print(f"Lendo arquivo Excel: {arquivo_excel}")
        
        # Ler o arquivo Excel
        df = pd.read_excel(arquivo_excel)
        print(f"Total de registros encontrados no Excel: {len(df)}")
        
        # Verificar as colunas do DataFrame
        print("Colunas encontradas:", df.columns.tolist())
        
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
                if i % 100 == 0:
                    print(f"Processados {i+1} registros...")
            except Exception as e:
                print(f"Erro ao processar registro {i}: {e}")
                print(f"Dados da linha: {row.to_dict()}")
        
        print(f"Total de registros processados: {len(registros)}")
        
        # Enviar dados para o Parse Server
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Primeiro, limpar a classe existente
            print("Verificando se a classe já existe...")
            try:
                response = await client.get(
                    f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                    headers=PARSE_HEADERS,
                    params={"limit": 1}
                )
                
                if response.status_code == 200:
                    print("Classe existe. Removendo registros existentes...")
                    # Remover todos os registros atuais
                    # Obter todos os objectIds
                    all_objects_response = await client.get(
                        f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                        headers=PARSE_HEADERS,
                        params={"limit": 1000}  # O Parse Server limita a 1000 registros por requisição
                    )
                    
                    if all_objects_response.status_code == 200:
                        objects = all_objects_response.json().get("results", [])
                        print(f"Encontrados {len(objects)} registros a serem removidos")
                        
                        # Remover cada registro
                        for obj in objects:
                            object_id = obj.get("objectId")
                            delete_response = await client.delete(
                                f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}/{object_id}",
                                headers=PARSE_HEADERS
                            )
                            
                            if delete_response.status_code != 200:
                                print(f"Erro ao remover registro {object_id}: {delete_response.status_code}")
                        
                        print("Registros removidos com sucesso!")
                    else:
                        print(f"Erro ao obter registros existentes: {all_objects_response.status_code}")
                else:
                    print(f"Classe não encontrada ou erro ao verificar: {response.status_code}")
            except Exception as e:
                print(f"Erro ao limpar registros existentes: {e}")
            
            # Inserir novos registros
            print("Inserindo novos registros...")
            inserted = 0
            errors = 0
            
            # Inserir em lotes de 50 para não sobrecarregar a API
            batch_size = 50
            for i in range(0, len(registros), batch_size):
                batch = registros[i:i+batch_size]
                print(f"Processando lote de {len(batch)} registros ({i+1} a {i+len(batch)} de {len(registros)})...")
                
                for registro in batch:
                    try:
                        response = await client.post(
                            f"{PARSE_SERVER_URL}/classes/{PRESENCA_CLASS}",
                            headers=PARSE_HEADERS,
                            json=registro
                        )
                        
                        if response.status_code == 201:
                            inserted += 1
                            if inserted % 20 == 0:
                                print(f"Inseridos {inserted} registros...")
                        else:
                            errors += 1
                            print(f"Erro ao inserir registro: {response.status_code} {response.text}")
                    except Exception as e:
                        errors += 1
                        print(f"Exceção ao inserir registro: {e}")
            
            print(f"Importação concluída! Inseridos {inserted} registros, {errors} erros.")
            return True
            
    except Exception as e:
        print(f"Erro durante a importação: {e}")
        return False

# Função principal
async def main():
    # Caminhos possíveis para o arquivo Excel
    caminhos = [
        "data/Frequencia Hack.xlsx",       # No diretório data/
        "Frequencia Hack.xlsx",            # Na raiz
        "../data/Frequencia Hack.xlsx",    # Um nível acima
        "../../data/Frequencia Hack.xlsx", # Dois níveis acima
    ]
    
    # Tentar cada caminho possível
    for caminho in caminhos:
        if os.path.exists(caminho):
            print(f"Arquivo encontrado em: {caminho}")
            sucesso = await importar_excel(caminho)
            if sucesso:
                print("Importação concluída com sucesso!")
            else:
                print("Falha na importação.")
            break
    else:
        print("Arquivo Excel não encontrado em nenhum dos caminhos verificados.")
        print("Caminhos verificados:")
        for caminho in caminhos:
            print(f"  - {caminho}")
        print("Diretório atual:", os.getcwd())
        print("Conteúdo do diretório atual:", os.listdir("."))
        if os.path.exists("data"):
            print("Conteúdo do diretório 'data':", os.listdir("data"))

# Executar o script
if __name__ == "__main__":
    asyncio.run(main())
