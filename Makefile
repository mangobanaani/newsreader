.PHONY: help install install-backend install-frontend dev stop seed-db add-feeds fetch-articles run-backend run-frontend test test-backend test-frontend test-e2e test-e2e-ui test-e2e-headed test-e2e-debug lint lint-backend lint-frontend format format-backend format-frontend type-check docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make seed-db          - Create admin user in database (admin@newsreader.local / admin123)"
	@echo "  make add-feeds        - Add default RSS feeds (BBC, Guardian, TechCrunch, etc.)"
	@echo "  make fetch-articles   - Fetch latest articles from all RSS feeds"
	@echo "  make dev              - Run both backend and frontend in parallel (kills existing processes first)"
	@echo "  make stop             - Stop all dev servers"
	@echo "  make run-backend      - Run backend development server only"
	@echo "  make run-frontend     - Run frontend development server only"
	@echo "  make test             - Run all tests (backend, frontend, e2e)"
	@echo "  make test-e2e         - Run Playwright end-to-end tests (headless)"
	@echo "  make test-e2e-ui      - Run Playwright tests with UI mode"
	@echo "  make test-e2e-headed  - Run Playwright tests in headed mode (visible browser)"
	@echo "  make test-e2e-debug   - Run Playwright tests in debug mode"
	@echo "  make lint             - Run all linters"
	@echo "  make format           - Format all code"
	@echo "  make type-check       - Run type checking"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make clean            - Clean build artifacts"

install: install-backend install-frontend

install-backend:
	cd backend && python -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

seed-db:
	@echo "Creating admin user in database..."
	cd backend && python seed_db.py

add-feeds:
	@echo "Adding default RSS feeds..."
	cd backend && python add_default_feeds.py

fetch-articles:
	@echo "Fetching articles from RSS feeds..."
	cd backend && python fetch_articles.py

dev:
	@echo "Cleaning up any existing dev servers..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@pkill -f "node.*vite" 2>/dev/null || true
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3001 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3002 | xargs kill -9 2>/dev/null || true
	@sleep 1
	@echo ""
	@echo "Starting backend and frontend development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000 (or next available port)"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@trap 'kill 0' EXIT; \
	(cd backend && . venv/bin/activate && DATABASE_URL="sqlite:///./dev.db" SECRET_KEY="dev-secret-key" ENABLE_LLM_FEATURES=true DEFAULT_LLM_PROVIDER=openai OPENAI_API_KEY="$$(grep OPENAI_API_KEY .env | cut -d= -f2)" uvicorn app.main:app --reload --reload-exclude 'tests/*' --host 0.0.0.0 --port 8000) & \
	(source ~/.nvm/nvm.sh && nvm use 22 && cd frontend && npm run dev) & \
	wait

stop:
	@echo "Stopping all development servers..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@pkill -f "node.*vite" 2>/dev/null || true
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3001 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3002 | xargs kill -9 2>/dev/null || true
	@echo "All dev servers stopped."

run-backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --reload-exclude 'tests/*' --host 0.0.0.0 --port 8000

run-frontend:
	source ~/.nvm/nvm.sh && nvm use 22 && cd frontend && npm run dev

test: test-backend test-frontend test-e2e

test-backend:
	cd backend && . venv/bin/activate && DATABASE_URL="sqlite:///./test.db" SECRET_KEY="test-secret-key-for-testing-only" pytest -v --cov=app --cov-report=html --cov-report=term

test-frontend:
	@echo "Running frontend unit tests..."
	cd frontend && npm run test -- --run

test-e2e:
	@echo "Running Playwright end-to-end tests..."
	cd frontend && npx playwright test

test-e2e-ui:
	@echo "Running Playwright tests in UI mode..."
	@echo "This will open an interactive browser window where you can:"
	@echo "  - Select tests to run"
	@echo "  - Watch tests execute step-by-step"
	@echo "  - Debug with time-travel"
	cd frontend && npx playwright test --ui

test-e2e-headed:
	@echo "Running Playwright tests in headed mode (visible browser)..."
	cd frontend && npx playwright test --headed

test-e2e-debug:
	@echo "Running Playwright tests in debug mode..."
	@echo "This will pause execution and open Playwright Inspector."
	cd frontend && npx playwright test --debug

lint: lint-backend lint-frontend

lint-backend:
	cd backend && . venv/bin/activate && \
	black --check app tests && \
	isort --check-only app tests && \
	flake8 app tests && \
	mypy app

lint-frontend:
	cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
	cd backend && . venv/bin/activate && \
	black app tests && \
	isort app tests

format-frontend:
	cd frontend && npm run format

type-check:
	cd backend && . venv/bin/activate && mypy app
	cd frontend && npm run type-check

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	cd frontend && rm -rf dist node_modules 2>/dev/null || true
