# GitHub Actions CI/CD Guide

## Complete CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  # Skip CI for documentation-only changes
  check-skip:
    runs-on: ubuntu-latest
    outputs:
      skip: ${{ steps.check.outputs.skip }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - id: check
        run: |
          FILES=$(git diff --name-only HEAD^ HEAD)
          if echo "$FILES" | grep -qvE '\.(md|txt)$|^\.claude/|^\.spec/|^docs/'; then
            echo "skip=false" >> $GITHUB_OUTPUT
          else
            echo "skip=true" >> $GITHUB_OUTPUT
          fi

  # Test job (Node.js example)
  test:
    needs: check-skip
    if: needs.check-skip.outputs.skip == 'false'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

  # Test job (Python example)
  test-python:
    needs: check-skip
    if: needs.check-skip.outputs.skip == 'false'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Run tests
        run: pytest --cov=src tests/

      - name: Build
        run: python -m build
```

## Deployment Workflows

### Vercel Deployment

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### Railway Deployment

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: ${{ secrets.RAILWAY_SERVICE }}
```

### AWS ECS Deployment

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        run: |
          docker build -t my-app .
          docker tag my-app:latest ${{ secrets.ECR_REPOSITORY }}:latest
          docker push ${{ secrets.ECR_REPOSITORY }}:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster my-cluster \
            --service my-service \
            --force-new-deployment
```

### Fly.io Deployment

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### NPM Package Publishing

```yaml
  publish:
    needs: test
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'

      - run: npm ci
      - run: npm run build
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Chrome Extension Release

```yaml
  release:
    needs: test
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - run: npm ci
      - run: npm run build

      - name: Package extension
        run: zip -r extension.zip dist/

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false

      - name: Upload Release Asset
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./extension.zip
          asset_name: extension.zip
          asset_content_type: application/zip
```

## Secrets Configuration

### Required Secrets by Platform

**Vercel:**
- `VERCEL_TOKEN` - From Vercel account settings
- `VERCEL_ORG_ID` - From project settings
- `VERCEL_PROJECT_ID` - From project settings

**Railway:**
- `RAILWAY_TOKEN` - From Railway account settings
- `RAILWAY_SERVICE` - Service ID from Railway

**AWS:**
- `AWS_ACCESS_KEY_ID` - IAM user access key
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key
- `ECR_REPOSITORY` - ECR repository URI

**Fly.io:**
- `FLY_API_TOKEN` - From Fly.io account settings

**NPM:**
- `NPM_TOKEN` - From npmjs.com account settings

### How to Add Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Reference in workflow: `${{ secrets.SECRET_NAME }}`

## Workflow Optimization

### Matrix Strategy (Test Multiple Versions)

```yaml
test:
  strategy:
    matrix:
      node-version: [18, 20, 22]
      os: [ubuntu-latest, windows-latest, macos-latest]
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
    - run: npm ci
    - run: npm test
```

### Caching Dependencies

Dependencies are automatically cached with `actions/setup-node@v4` and `actions/setup-python@v5` when using `cache` parameter.

### Conditional Jobs

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/dev'
  # ... deploy to staging

deploy-production:
  if: github.ref == 'refs/heads/main'
  # ... deploy to production
```

## Common Patterns

**Skip CI on specific paths:**
```yaml
on:
  push:
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.claude/**'
```

**Run on schedule (cron):**
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
```

**Manual trigger:**
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

## Troubleshooting

**Secrets not found:**
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to repository (not organization)
- For organization secrets, check repository access

**Cache not working:**
- Verify `cache` parameter is set in setup action
- Check lock file (package-lock.json, requirements.txt) is committed

**Deploy fails but tests pass:**
- Check deployment secrets are configured
- Verify deployment target is accessible
- Check logs in deployment platform
