import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from utils import carregar_dados_excel, buscar_presenca
from file_check import check_files  # Importa a função de verificação

# Inicializar o aplicativo FastAPI com configurações explícitas
app = FastAPI(
    title="Consulta Presença QR Code Hack Barão 2025",
    docs_url=None,  # Desativa o Swagger UI
    redoc_url=None,  # Desativa o ReDoc
)

# Adicionar CORS middleware para permitir solicitações de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar diretórios para templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Evento de inicialização
@app.on_event("startup")
async def startup_db_client():
    # Verificar os arquivos disponíveis
    check_files()
    
    # Continuar com a inicialização normal
    await init_db()
    try:
        await carregar_dados_excel()
    except Exception as e:
        print(f"Erro ao carregar dados do Excel: {e}")

# Rota principal - página inicial
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print(f"Acessando rota principal com URL base: {request.base_url}")
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "titulo": "Consulta presença QR Code Hack Barão 2025"}
    )

# Rota alternativa (caso haja problema com a rota principal)
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    print(f"Acessando rota /home com URL base: {request.base_url}")
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "titulo": "Consulta presença QR Code Hack Barão 2025"}
    )

# Rota para consultar presença
@app.post("/consultar", response_class=HTMLResponse)
async def consultar(request: Request, codigo: str = Form(...)):
    try:
        print(f"Consultando código: {codigo}")
        # Converter código para inteiro
        id_estudante = int(codigo)
        
        # Buscar dados de presença
        resultado = await buscar_presenca(id_estudante)
        
        if resultado:
            return templates.TemplateResponse(
                "resultado.html", 
                {
                    "request": request, 
                    "titulo": "Resultado da Consulta", 
                    "nome": f"{resultado['nome']} {resultado['sobrenome']}",
                    "presencas": resultado["presencas"],
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
        print(f"Erro ao consultar: {str(e)}")
        return templates.TemplateResponse(
            "resultado.html", 
            {
                "request": request, 
                "titulo": "Erro", 
                "encontrado": False,
                "mensagem": f"Ocorreu um erro: {str(e)}"
            }
        )

# Rota para verificar a saúde da aplicação (útil para monitoramento)
@app.get("/health")
async def health():
    return {"status": "ok"}

# Rota para listar arquivos (útil para debug)
@app.get("/files")
async def list_files():
    """Endpoint para listar arquivos disponíveis"""
    from file_check import listar_arquivos
    
    files = listar_arquivos()
    return {"files": files, "count": len(files)}

# Endpoint para testar o Parse Server
@app.get("/test-parse")
async def test_parse():
    """Endpoint para testar a conexão com o Parse Server"""
    from database import test_connection
    
    try:
        result = await test_connection()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================
# INÍCIO DO SERVIDOR
# ============================

if __name__ == "__main__":
    import uvicorn
    # Obter porta do ambiente ou usar 8000 como padrão
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
