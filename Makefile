.PHONY: up down logs migrate seed valuate test lint clean

# ── Docker ────────────────────────────────────────────────────────────────────

up:
	docker compose -f infra/docker-compose.yml up -d
	@echo "✓ Postgres + Redis running"

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f

# ── Backend ───────────────────────────────────────────────────────────────────

install:
	cd backend && pip install -r requirements.txt

migrate:
	cd backend && source .venv/bin/activate && alembic upgrade head
	@echo "✓ Migrations applied"

seed:
	cd backend && source .venv/bin/activate && cd .. && python data/seeds/seed.py --count 1500
	@echo "✓ Seeded 1500 listings"

seed-reset:
	cd backend && source .venv/bin/activate && cd .. && python data/seeds/seed.py --count 1500 --reset
	@echo "✓ Reset and re-seeded"

valuate:
	cd backend && source .venv/bin/activate && cd .. && python data/valuate.py
	@echo "✓ Valuations and deal scores computed"

# ── Dev server ────────────────────────────────────────────────────────────────

dev:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	cd backend && source .venv/bin/activate && pytest tests/ -v

test-fast:
	cd backend && source .venv/bin/activate && pytest tests/ -x -q

# ── Utilities ─────────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned pycache"

psql:
	docker exec -it luxemarket_db psql -U luxe -d luxemarket

redis-cli:
	docker exec -it luxemarket_redis redis-cli

# ── Full bootstrap (for new clone) ───────────────────────────────────────────

bootstrap: up migrate seed valuate
	@echo ""
	@echo "✓ LuxeMarket stack is ready!"
	@echo "  Run: make dev"
	@echo "  Open: http://localhost:8000/docs"


# Clear Redis cache
cache-clear:
	curl -s -X DELETE http://localhost:8000/api/v1/cache | python -m json.tool

# Trigger valuation job via API
valuate-api:
	curl -s -X POST http://localhost:8000/api/v1/jobs/valuate | python -m json.tool
	@echo "Check status with: curl http://localhost:8000/api/v1/jobs/valuate/status"

# Open API docs
docs:
	open http://localhost:8000/docs