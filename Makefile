.PHONY: dev backend frontend

dev:
	./scripts/dev.sh

backend:
	cd backend && \
	if [ -x .venv/bin/python ]; then \
		.venv/bin/python -m uvicorn app.main:app --reload --port 8000; \
	else \
		uvicorn app.main:app --reload --port 8000; \
	fi

frontend:
	cd frontend && npm run dev -- --port 5173
