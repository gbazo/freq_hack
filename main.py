import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from database import init_db  # Removido o prefixo "app."
from utils import carregar_dados_excel, buscar_presenca  # Removido o prefixo "app."

# Inicializar o aplicativo FastAPI
app = FastAPI(title="Consulta Presença QR Code Hack Barão 2025")

# Configurar diretórios para templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")  # Caminho ajustado

# Evento de inicialização
@app.on_event("startup")
async def startup_db_client():
    await init_db()
    try:
        await carregar_dados_excel()
    except Exception as e:
        print(f"Erro ao carregar dados do Excel: {e}")

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

# ============================
# INÍCIO DO SERVIDOR
# ============================

if __name__ == "__main__":
    import uvicorn
    # Obter porta do ambiente ou usar 8000 como padrão
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
