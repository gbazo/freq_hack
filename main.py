from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import database

# Inicializar o aplicativo FastAPI
app = FastAPI(title="Consulta Presença QR Code Hack Barão 2025")

# Configurar diretórios para templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Evento de inicialização
@app.on_event("startup")
async def startup_db_client():
    # Inicializar conexão com o Parse Server
    if await database.init_db():
        # Se a conexão for bem-sucedida, carregar dados do Excel
        await database.carregar_excel()

# Rota principal - página inicial
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "titulo": "Consulta presença QR Code Hack Barão 2025"}
    )

# Rota para consultar presença
@app.post("/consultar", response_class=HTMLResponse)
async def consultar(request: Request, codigo: str = Form(...)):
    try:
        # Converter código para inteiro
        id_estudante = int(codigo)
        
        # Buscar dados de presença
        aluno = await database.buscar_aluno(id_estudante)
        
        if aluno:
            return templates.TemplateResponse(
                "resultado.html", 
                {
                    "request": request, 
                    "titulo": "Resultado da Consulta", 
                    "nome": f"{aluno['nome']} {aluno['sobrenome']}",
                    "presencas": aluno['presencas'],
                    "encontrado": True
                }
            )
        else:
            return templates.TemplateResponse(
                "resultado.html", 
                {
                    "request": request, 
                    "titulo": "Resultado da Consulta", 
                    "encontrado": False,
                    "mensagem": "Nenhum aluno encontrado com este código."
                }
            )
    except ValueError:
        return templates.TemplateResponse(
            "resultado.html", 
            {
                "request": request, 
                "titulo": "Erro", 
                "encontrado": False,
                "mensagem": "Código inválido. Digite apenas números."
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "resultado.html", 
            {
                "request": request, 
                "titulo": "Erro", 
                "encontrado": False,
                "mensagem": f"Ocorreu um erro: {str(e)}"
            }
        )

# Rota para verificar a saúde da aplicação
@app.get("/health")
async def health():
    return {"status": "ok"}

# Rota para testar a conexão com o Parse Server
@app.get("/test-parse")
async def test_parse():
    try:
        # Inicializar conexão com o Parse Server
        result = await database.init_db()
        return {"status": "success" if result else "error", "connected": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Rota para forçar o carregamento do Excel
@app.get("/load-excel")
async def load_excel():
    try:
        result = await database.carregar_excel()
        return {
            "status": "success",
            "message": "Dados do Excel carregados com sucesso" if result else "Arquivo Excel não encontrado, usando dados de exemplo"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
