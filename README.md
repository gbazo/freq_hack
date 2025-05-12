# Sistema de Consulta de Presença - Hack Barão 2025

Este sistema web permite que os alunos consultem suas presenças no evento "Hack Barão 2025" utilizando seu número de identificação (RA). Desenvolvido com FastAPI e hospedado no Back4App com MongoDB como banco de dados.

## 📋 Características

- Página inicial simples para entrada do número de identificação do aluno
- Exibição do status de presença para cada dia e horário do evento
- Importação de dados a partir de planilha Excel
- API RESTful para consulta e administração
- Deploy fácil no Back4App

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI (Python 3.11)
- **Banco de Dados**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **Processamento de Dados**: Pandas, openpyxl
- **Deploy**: Docker, Back4App

## 🗂️ Estrutura do Projeto

```
projeto/
│
├── templates/           # Templates HTML
│   ├── index.html       # Página inicial
│   └── resultado.html   # Página de resultado da consulta
│
├── static/              # Arquivos estáticos
│   ├── style.css        # Estilos CSS
│   └── script.js        # Scripts JavaScript
│
├── data/                # Pasta para dados
│   └── Frequencia Hack.xlsx  # Planilha com dados de presença
│
├── database.py          # Módulo de conexão com o Parse Server
├── import_excel.py      # Script para importação da planilha
├── main.py              # Aplicação FastAPI principal
├── Dockerfile           # Configuração para Docker
├── requirements.txt     # Dependências do projeto
├── .gitignore           # Arquivos a serem ignorados pelo Git
└── README.md            # Este arquivo
```

## 🚀 Como Executar

### Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/freq_hack.git
   cd freq_hack
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   uvicorn main:app --reload
   ```

4. Acesse a aplicação em `http://localhost:8000`

### Deploy no Back4App

1. Crie uma conta no [Back4App](https://back4app.com/)
2. Crie um novo aplicativo e configure o Parse Server
3. Obtenha as chaves de acesso (Application ID e REST API Key)
4. Configure as variáveis de ambiente no Back4App:
   - `PARSE_APP_ID`
   - `PARSE_REST_API_KEY`
   - `PARSE_SERVER_URL`
5. Conecte seu repositório GitHub e faça o deploy

## 🛠️ Scripts de Utilitários

### Importação de Dados

Para importar dados da planilha Excel diretamente:

```bash
python import_excel.py
```

Este script:
1. Procura a planilha em vários locais possíveis
2. Remove registros existentes no Parse Server
3. Importa todos os dados da planilha

## 📄 Licença

Este projeto está licenciado sob a Licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

Desenvolvido por Gabriel Bazo para o evento Hack Barão 2025.
