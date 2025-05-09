from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Inicializar o aplicativo FastAPI
app = FastAPI(title="Consulta Presença QR Code Hack Barão 2025")

# Configurar diretórios para templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dados em memória para demonstração
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

# Rota principal - página inicial
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "titulo": "Consulta presença QR Code Hack Barão 2025"}
    )

# Rota para consultar presença (usando dados em memória)
@app.post("/consultar", response_class=HTMLResponse)
async def consultar(request: Request, codigo: str = Form(...)):
    try:
        # Converter código para inteiro
        id_estudante = int(codigo)
        
        # Buscar dados de presença nos dados de exemplo
        if id_estudante in DADOS_EXEMPLO:
            aluno = DADOS_EXEMPLO[id_estudante]
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
