# Variáveis
APP_NAME = phyton_app
DOCKER_IMAGE = myapp-image
DOCKER_CONTAINER = python-whatsapp-bot
PYTHON = python3

# Use o comando docker-compose se tiver (ajuste conforme seu setup)
DOCKER_COMPOSE = docker-compose

# Variáveis para banco e migrações
ALEMBIC = alembic
DB_URI = ${ASYNC_DATABASE_URI}

# Cria o ambiente virtual (caso não esteja usando Docker)
venv:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip setuptools wheel
	.venv/bin/pip install -r requirements.txt

# Rodar o app (modo dev) dentro do container Docker
run:
	docker-compose up

# Entrar no shell do container
shell:
	docker exec -it $(DOCKER_CONTAINER) /bin/bash

# Rodar migrações alembic (upgrade até o head)
alembic-upgrade:
	docker-compose exec python_app alembic upgrade head

# Criar nova migration (passar MESSAGE como argumento)
alembic-revision:
	docker-compose alembic revision --autogenerate -m "$(MSG)"

# Rodar testes (ajuste comando de testes)
test:
	docker exec -it $(DOCKER_CONTAINER) pytest tests/

# Limpar containers, volumes, redes criados pelo docker-compose
clean:
	docker-compose down -v --remove-orphans

.PHONY: venv run shell alembic-upgrade alembic-revision test clean
