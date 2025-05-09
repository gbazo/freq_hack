import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter URL de conexão do MongoDB de variáveis de ambiente ou usar um valor padrão
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hack_barao_2025")

# Cliente MongoDB
client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
db = client[DB_NAME]

# Coleção para armazenar os dados de presença
presenca_collection = db.presencas

# Função para inicializar o banco de dados
async def init_db():
    try:
        # Verificar a conexão com o MongoDB
        await client.admin.command('ping')
        print("Conexão com MongoDB estabelecida com sucesso!")
        
        # Criar índice no campo ID do Estudante para pesquisas mais rápidas
        await presenca_collection.create_index("id_estudante")
        
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        raise