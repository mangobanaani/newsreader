# Contributing to NewsReader

Thank you for your interest in contributing to NewsReader! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Accept criticism gracefully
- Prioritize the community and project goals

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/newsreader.git
   cd newsreader
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream git@github.com:mangobanaani/newsreader.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 22+
- SQLite (for development) or PostgreSQL (for production)
- Git

### Installation

```bash
# Install all dependencies
make install

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Initialize database
make seed-db

# Add sample feeds
make add-feeds

# Fetch initial articles
make fetch-articles
```

### Running the Development Servers

```bash
# Start both backend and frontend
make dev

# Or run them separately:
make run-backend  # Backend on http://localhost:8000
make run-frontend # Frontend on http://localhost:3000
```

## Development Workflow

1. **Sync with upstream** before starting work:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the coding standards

4. **Test your changes**:
   ```bash
   make test          # Run all tests
   make lint          # Check code style
   make type-check    # Run type checking
   ```

5. **Commit your changes** following commit guidelines

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting
- Use mypy for type checking

```bash
# Format code
make format-backend

# Check style
make lint-backend
```

### TypeScript/React (Frontend)

- Follow ESLint configuration
- Use TypeScript strict mode
- Use functional components with hooks
- Use meaningful variable and function names
- Maximum line length: 100 characters
- Use Prettier for code formatting

```bash
# Format code
make format-frontend

# Check style
make lint-frontend

# Type check
npm run type-check
```

### General Guidelines

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Avoid code duplication
- Use meaningful names for variables, functions, and classes
- Write unit tests for new features
- Update documentation when changing functionality

## Testing Guidelines

### Backend Tests

- Write tests using pytest
- Aim for high test coverage (target: 80%+)
- Test both success and error cases
- Use fixtures for common test data
- Mock external dependencies

```bash
# Run backend tests
make test-backend

# Run with coverage
cd backend && pytest --cov=app --cov-report=html
```

### Frontend Tests

- Write unit tests using Vitest
- Write component tests using React Testing Library
- Write E2E tests using Playwright for critical flows
- Test user interactions and edge cases

```bash
# Run frontend unit tests
make test-frontend

# Run E2E tests
make test-e2e-ui  # Interactive mode
make test-e2e     # Headless mode
```

### Test Organization

- Place unit tests next to the code they test
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert
- Keep tests independent and isolated

## Commit Guidelines

We follow conventional commit messages for clarity and automatic changelog generation.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process or tooling changes
- **perf**: Performance improvements

### Examples

```
feat(auth): add Google OAuth login support

Implement Google OAuth authentication as an alternative to email/password login.
Users can now sign in with their Google account.

Closes #123
```

```
fix(api): handle null values in article sentiment

Fixed TypeError when processing articles with null sentiment scores.
Now properly handles null values and defaults to neutral sentiment.
```

```
docs: update installation instructions

Added troubleshooting section and clarified Node.js version requirements.
```

## Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass**:
   ```bash
   make test
   make lint
   ```
4. **Update CHANGELOG.md** (if applicable)
5. **Fill out the PR template** with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (for UI changes)
6. **Request review** from maintainers
7. **Address review feedback** promptly
8. **Squash commits** if requested before merging

### PR Checklist

- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts with main
- [ ] PR description is clear and complete

## Reporting Bugs

When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the problem
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details**:
   - OS version
   - Python version
   - Node.js version
   - Browser (for frontend issues)
6. **Error messages** or screenshots
7. **Possible solution** (if you have ideas)

Use the GitHub issue template for bug reports.

## Suggesting Features

When suggesting features, please include:

1. **Clear description** of the feature
2. **Use case** - why is this needed?
3. **Proposed solution** - how should it work?
4. **Alternatives considered**
5. **Additional context** - mockups, examples, etc.

Use the GitHub issue template for feature requests.

## Project Structure

```
newsreader/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality (auth, config)
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   └── tests/            # Backend tests
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # React contexts
│   │   └── store/        # State management
│   └── tests/            # Frontend tests
└── docs/                 # Documentation
```

## Need Help?

- Check existing [issues](https://github.com/mangobanaani/newsreader/issues)
- Read the [README](README.md) and other documentation
- Ask questions in [discussions](https://github.com/mangobanaani/newsreader/discussions)

## License

By contributing to NewsReader, you agree that your contributions will be licensed under the GNU General Public License v3.0.

Thank you for contributing to NewsReader!
