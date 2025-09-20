# Aplicativo de Monitoramento do Preço do Bitcoin

Este projeto é um pipeline de preços do Bitcoin. Utiliza FastAPI para criar uma API que fornece dados de preço do Bitcoin. A aplicação coleta preços do Bitcoin em segundo plano e os armazena em um banco de dados PostgreSQL. A API expõe endpoints para recuperar o preço mais recente, o histórico de preços e estatísticas de preços.

## Estrutura do Projeto

```
/home/zambra/git/usage-overarch-halogen/
├───.env.example
├───.gitignore
├───CLAUDE.md
├───init.sql
├───poetry.lock
├───pyproject.toml
├───README.md
├───requirements.txt
├───.git/...
├───docker/
│   └───docker-compose.yml
├───docs/
├───scripts/
│   └───install-mcp-servers.sh
├───src/
│   ├───__init__.py
│   ├───main.py
│   ├───api/
│   │   ├───__init__.py
│   │   └───routes/
│   ├───core/
│   │   ├───__init__.py
│   │   ├───database.py
│   │   └───__pycache__/
│   ├───models/
│   │   ├───__init__.py
│   │   ├───database.py
│   │   ├───schemas.py
│   │   └───__pycache__/
│   ├───services/
│   │   ├───__init__.py
│   │   ├───databricks.py
│   │   ├───price_collector.py
│   │   └───__pycache__/
│   └───utils/
│       └───__init__.py
└───tests/
    ├───__init__.py
    ├───test_api/
    └───test_services/
```

## Explicação do Código

- **`src/main.py`**: Ponto de entrada da aplicação FastAPI. Define os endpoints da API e gerencia a tarefa de coleta de preços em background.  
- **`src/services/price_collector.py`**: Serviço responsável por coletar os preços do Bitcoin a partir de uma fonte externa.  
- **`src/core/database.py`**: Gerencia a conexão com o banco de dados e as sessões.  
- **`src/models/database.py`**: Define o modelo do banco de dados (SQLAlchemy) para armazenar os preços do Bitcoin.  
- **`src/models/schemas.py`**: Define os schemas (Pydantic) para validação dos dados de requisições e respostas da API.  
- **`docker/docker-compose.yml`**: Define o serviço PostgreSQL para o banco de dados.  
- **`pyproject.toml`**: Define as dependências do projeto e metadados.

## Como Executar

1.  **Configurar o ambiente:**
    - Crie um arquivo `.env` a partir de `.env.example` e preencha com as credenciais do seu banco de dados.
2.  **Iniciar os serviços:**
    - Execute `docker-compose up -d` para iniciar o banco de dados PostgreSQL.
3.  **Instalar dependências:**
    - Execute `poetry install` para instalar as dependências do projeto.
4.  **Executar a aplicação:**
    - Execute `poetry run uvicorn src.main:app --reload` para iniciar a aplicação FastAPI.
