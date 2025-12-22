# Docker Setup Guide

## When to Use Docker

Use Docker when:
- Project needs consistent development environment across team
- Deploying to containerized platforms (Fly.io, Railway, AWS ECS)
- Need to isolate dependencies or services
- Want to match production environment locally

## Dockerfile Examples

### Development Dockerfile

For local development with hot reload:

**Node.js:**
```dockerfile
FROM node:20-alpine
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start dev server
CMD ["npm", "run", "dev"]
```

**Python:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Start dev server
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0"]
```

### Production Dockerfile (Multi-stage Build)

For optimized production images:

**Node.js (Next.js):**
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public

# Run as non-root user (security)
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

EXPOSE 3000
CMD ["npm", "start"]
```

**Python (FastAPI):**
```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Add dependencies to PATH
ENV PATH=/root/.local/bin:$PATH

# Run as non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

## docker-compose.yml

For local development with services:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules  # Prevent overwriting node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## .dockerignore

Always create `.dockerignore` to reduce build context size:

```
# Dependencies
node_modules/
__pycache__/
venv/
.venv/

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# Environment
.env
.env.*

# Build artifacts
dist/
build/
.next/

# Tests
coverage/
*.test.ts
test_*.py

# Documentation
*.md
.claude/
docs/
```

## Common Docker Commands

```bash
# Build image
docker build -t myapp .

# Run container
docker run -p 3000:3000 myapp

# Run with environment variables
docker run -p 3000:3000 --env-file .env myapp

# Use docker-compose
docker-compose up        # Start all services
docker-compose up -d     # Start in background
docker-compose down      # Stop and remove containers
docker-compose logs      # View logs
```

## Best Practices

1. **Use multi-stage builds** for production (smaller images)
2. **Run as non-root user** for security
3. **Use alpine images** when possible (smaller, faster)
4. **Cache dependencies** by copying package files first
5. **Use .dockerignore** to exclude unnecessary files
6. **Pin versions** (node:20-alpine, not node:latest)
7. **Add healthchecks** for production containers

## Troubleshooting

**Build fails - can't find dependencies:**
- Check package.json/requirements.txt is copied before RUN npm install
- Verify file paths in COPY commands

**Container works locally but fails in production:**
- Check environment variables are set
- Verify ports are exposed correctly
- Check file permissions (especially if using non-root user)

**Image too large:**
- Use alpine base images
- Use multi-stage builds
- Add more files to .dockerignore
- Remove build dependencies in production stage
