import pandas as pd
import os
from database import presenca_collection
from models import Presenca

# Mapeamento de status
STATUS_MAP = {
    0: "Ausente",
    1: "Presente",
    2: "Data Futura"
}

# Função para carregar dados do Excel para o Parse Server
async def carregar_dados_excel():
    # Caminho para o arquivo Excel
    excel_path = os.path.join("data", "Frequencia Hack.xlsx")
    
    # Verificar se o arquivo existe
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Arquivo Excel não encontrado: {excel_path}")
    
    # Ler o arquivo Excel
    df = pd.read_excel(excel_path)
    
    # Verificar se já existem dados no Parse Server
    count = await presenca_collection.count_documents()
    if count > 0:
        print("Dados já existem no Parse Server. Pulando importação.")
        return
    
    # Preparar dados para inserção no Parse Server
    dados = []
    for _, row in df.iterrows():
        presenca = {
            "id_estudante": int(row["ID do Estudante"]),
            "nome": row["Nome"],
            "sobrenome": row["Sobrenome"],
            "email": row["Endereço de email"],
            "dia_07_05": int(row["7/05/2025"]),
            "dia_08_05_19h": int(row["8/05/2025 19:00 "]),
            "dia_08_05_20h": int(row["8/05/2025 20:00"]),
            "dia_09_05_19h": int(row["9/05/2025 19:00 "]),
            "dia_09_05_20h": int(row["9/05/2025 20:00"])
        }
        dados.append(presenca)
    
    # Inserir dados no Parse Server
    if dados:
        await presenca_collection.insert_many(dados)
        print(f"{len(dados)} registros inseridos no Parse Server.")

# Função para obter os dados de presença de um aluno pelo ID
async def buscar_presenca(id_estudante: int):
    # Buscar no Parse Server
    query = {"id_estudante": id_estudante}
    resultado = await presenca_collection.find_one(query)
    
    if not resultado:
        return None
    
    # Formatar os resultados
    presencas = {
        "07/05/2025": STATUS_MAP[resultado["dia_07_05"]],
        "08/05/2025 19:00": STATUS_MAP[resultado["dia_08_05_19h"]],
        "08/05/2025 20:00": STATUS_MAP[resultado["dia_08_05_20h"]],
        "09/05/2025 19:00": STATUS_MAP[resultado["dia_09_05_19h"]],
        "09/05/2025 20:00": STATUS_MAP[resultado["dia_09_05_20h"]]
    }
    
    return {
        "nome": resultado["nome"],
        "sobrenome": resultado["sobrenome"],
        "presencas": presencas
    }
