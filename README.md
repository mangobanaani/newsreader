# NewsReader - AI-Powered News Aggregator

An intelligent news aggregation platform that uses NLP clustering, semantic analysis, and LLM-based recommendations to help you discover and organize relevant news articles.

## Screenshots

![Main Feed](screenshots/Screenshot%202025-11-03%20at%2022.08.39%20Medium.jpeg)
*Article feed with AI-powered insights and topic tags*

![Analytics Dashboard](screenshots/Screenshot%202025-11-03%20at%2022.24.51%20Medium.jpeg)
*Reading activity and engagement analytics*

![Sentiment Analysis](screenshots/Screenshot%202025-11-03%20at%2022.25.03%20Medium.jpeg)
*Sentiment overview and trending topics*

![Command Palette](screenshots/Screenshot%202025-11-03%20at%2022.26.17%20Medium.jpeg)
*Quick search and navigation with command palette*

![Bookmarks](screenshots/Screenshot%202025-11-03%20at%2022.31.23%20Medium.jpeg)
*Saved articles and bookmarks*

![Feed Management](screenshots/Screenshot%202025-11-03%20at%2022.31.43%20Medium.jpeg)
*Browse and activate RSS feeds*

![User Preferences](screenshots/Screenshot%202025-11-03%20at%2022.31.59%20Medium.jpeg)
*Customizable preferences and recommendations*

## Features

- **Google OAuth Login** - Sign in with Google (optional)
- **RSS Feed Management** - Subscribe to multiple RSS feeds
- **AI-Powered Insights** - Get summaries, key points, and reliability scores
- **Smart Recommendations** - Personalized article suggestions
- **Semantic Search** - Natural language article search
- **Auto-Tagging** - Automatic topic extraction
- **Sentiment Analysis** - Understand article tone
- **Article Clustering** - Group similar articles
- **Bookmarks & Reading Status** - Track your reading
- **Modern Dark UI** - Sleek interface with glass morphism

## Tech Stack

**Backend**: FastAPI · PostgreSQL · SQLAlchemy · OpenAI/Anthropic
**Frontend**: React 19 · TypeScript · Vite · TailwindCSS
**NLP**: sentence-transformers · VADER · scikit-learn
**Testing**: pytest · Vitest · Playwright

## Quick Start

```bash
# Install dependencies
make install

# Configure .env file
cp .env.example .env
# Edit .env with your API keys

# Initialize database
make seed-db        # Create admin user (admin@newsreader.local / admin123)
make add-feeds      # Add default RSS feeds  
make fetch-articles # Fetch initial articles

# Start development servers
make dev
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Commands

```bash
make install          # Install all dependencies
make dev              # Run both backend and frontend
make stop             # Stop all dev servers
make test             # Run all tests (backend + frontend + e2e)
make test-e2e         # Run Playwright e2e tests (headless)
make test-e2e-ui      # Run Playwright e2e tests (interactive UI)
make lint             # Run linters
make format           # Format code
make clean            # Remove build artifacts
```

For a full list of commands, run `make help`.

## Project Structure

```
newsreader/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── tests/    # Backend tests
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── api/      # API client
│   │   ├── components/ # React components
│   │   ├── pages/    # Page components
│   │   └── test/     # Unit tests
│   └── package.json
├── .github/workflows/ # CI/CD
├── Makefile          # Development commands
└── README.md         # This file
```

## Configuration

Create `.env` file:

```bash
# API Keys (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Google OAuth (Optional - see GOOGLE_OAUTH_SETUP.md)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Database
DATABASE_URL=sqlite:///./dev.db
# Or PostgreSQL: postgresql://user:pass@localhost:5432/newsreader

# Security
SECRET_KEY=your-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Settings  
ENABLE_LLM_FEATURES=true
DEFAULT_LLM_PROVIDER=openai
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register (disabled)

### Articles
- `GET /api/v1/articles/` - List articles
- `GET /api/v1/articles/{id}` - Get article
- `GET /api/v1/articles/{id}/llm-insights` - AI insights
- `GET /api/v1/articles/recommendations` - Recommendations

### Feeds
- `GET /api/v1/feeds/` - List feeds
- `POST /api/v1/feeds/` - Add feed
- `POST /api/v1/feeds/{id}/fetch` - Fetch articles

Full documentation: http://localhost:8000/docs

## Testing

```bash
# Run all tests (backend, frontend, e2e)
make test

# Backend tests
make test-backend

# Frontend unit tests
make test-frontend

# End-to-end tests with Playwright
make test-e2e              # Headless mode (CI/CD)
make test-e2e-ui           # Interactive UI mode (recommended for development)
make test-e2e-headed       # Visible browser mode
make test-e2e-debug        # Debug mode with Playwright Inspector
```

For detailed testing documentation, see [TESTING.md](./TESTING.md)

## Development

1. Start servers: `make dev`
2. Make changes (auto-reload enabled)
3. Run tests: `make test`
4. Check quality: `make lint`
5. Commit changes

## Troubleshooting

**Backend not starting:**
```bash
lsof -ti:8000 | xargs kill -9
make stop && make dev
```

**Wrong Node.js version:**
```bash
nvm install 22 && nvm use 22
```

**Database issues:**
```bash
rm backend/dev.db
make seed-db && make fetch-articles
```

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details

---

**Built using FastAPI, React, and AI**
