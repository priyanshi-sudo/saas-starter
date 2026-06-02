.PHONY: dev seed test backend worker

dev:
	docker compose up --build -d

seed:
	cd backend && python -m app.seed

backend:
	cd backend && uvicorn app.main:app --reload

worker:
	cd backend && arq app.workers.tasks.WorkerSettings

test:
	cd backend && pytest -q
