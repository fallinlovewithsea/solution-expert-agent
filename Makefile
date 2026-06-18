.PHONY: up down init-knowledge-base logs shell test

up:
	docker compose up -d

down:
	docker compose down

up-gpu:
	docker compose --profile gpu up -d

init-knowledge-base:
	docker compose exec orchestrator python scripts/init_knowledge_base.py

logs:
	docker compose logs -f orchestrator

shell:
	docker compose exec orchestrator bash

test:
	docker compose exec orchestrator pytest -v

pull-ollama:
	docker compose exec ollama ollama pull qwen2.5:7b