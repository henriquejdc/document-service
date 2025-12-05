# Document Service - FastAPI + MongoDB

Aplicação de exemplo para o desafio técnico: serviço REST em Python (FastAPI) que persiste documentos em MongoDB e 
permite buscas por palavra-chave/expressões e ordenação por proximidade geográfica.

Para melhor desempenho em buscas textuais, cria índices apropriados no MongoDB ao iniciar e utiliza consultas otimizadas.
Também implementa-se ordenação por proximidade geográfica usando índices geoespaciais, caso latitude e longitude sejam fornecidas.

## Documentação da API (Swagger)

A documentação interativa da API está disponível através do Swagger UI após iniciar a aplicação:

- **Swagger UI (Interativo)**: http://localhost:8000/docs ou http://localhost:8000
- **ReDoc (Alternativo)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Recursos do Swagger

- Interface interativa para testar todos os endpoints
- Exemplos de requisições e respostas
- Descrição detalhada de todos os parâmetros
- Schemas de dados com validações
- Códigos de resposta HTTP documentados

## Como rodar (com Docker):

Utilizou-se de Docker para facilitar o setup e execução caso prefira.


1. Build e start com docker-compose:

```bash
docker-compose up --build
```

2. A API ficará disponível em `http://localhost:8000`.

## Endpoints principais:

- `POST /documentos` — cria um documento (JSON). Campos obrigatórios: `titulo`, `autor`, `conteudo`, `data` (YYYY-MM-DD). `latitude` e `longitude` são opcionais (bônus).
- `GET /documentos?palavraChave=...` — busca por palavra (caso simples).
- `GET /documentos?busca=...` — busca por expressão (frase completa). Aceita opcionalmente `latitude` e `longitude` para ordenar por proximidade.

Observações:
- A aplicação usa MongoDB real (não em memória). Cria índices para busca por texto ao iniciar.
- Requisitos: Docker e Docker Compose ou fazer a instalação local.

## Executando local (sem Docker):

Para o setup e execução manual caso prefira.

1. Crie e ative um virtualenv Python 3.12.
2. Ambiente virtual (recomendado):

	1. Crie a venv e ative (Linux/macOS):

	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	```

	2. No Windows (PowerShell):

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	```
2. Instale dependências: `pip install -r requirements.txt`.
3. Exporte variáveis: `MONGO_URI` e `MONGO_DB` (opcionais, padrões em `docker-compose.yml`).
4. Rode: `uvicorn app.main:app --reload`.
