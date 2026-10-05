.PHONY: test backend frontend

test:
	python -m pytest

backend:
	uvicorn backend.src.main:app --reload

frontend:
	cd frontend && npm run dev
