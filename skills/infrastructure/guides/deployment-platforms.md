# Deployment Platforms Guide

## Platform Selection

Choose based on project type and requirements:

| Platform | Best For | Pricing | Setup Complexity |
|----------|----------|---------|------------------|
| **Vercel** | Next.js, React, static sites | Free tier generous | ⭐ Easy |
| **Railway** | Any framework, needs DB | $5/month (includes DB) | ⭐⭐ Medium |
| **Fly.io** | Global edge, low latency | Pay-as-you-go | ⭐⭐ Medium |
| **AWS** | Enterprise, full control | Complex pricing | ⭐⭐⭐⭐ Hard |
| **Custom VPS** | Claude Code, full control, multi-device | $5-15/month | ⭐⭐⭐ Medium-Hard |
| **Chrome Web Store** | Browser extensions | $5 one-time | ⭐ Easy |
| **NPM** | Node.js packages | Free | ⭐ Easy |

---

## Vercel

**Best for:** Next.js, React, static sites, serverless functions

**Setup:**
```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**CI/CD Integration:**
See [github-actions.md](github-actions.md#vercel-deployment) for GitHub Actions workflow.

**Environment Variables:**
```bash
# Via CLI
vercel env add OPENAI_API_KEY

# Or in dashboard: Settings → Environment Variables
```

**Features:**
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments for PRs
- ✅ Edge functions
- ✅ Built-in analytics

**Required Secrets:**
- `VERCEL_TOKEN` - Account settings → Tokens
- `VERCEL_ORG_ID` - Project settings → General
- `VERCEL_PROJECT_ID` - Project settings → General

---

## Railway

**Best for:** Full-stack apps with database, APIs, background jobs

**Setup:**
```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

**Add Database:**
```bash
railway add --database postgres
```

**Features:**
- ✅ PostgreSQL, MySQL, Redis, MongoDB included
- ✅ Automatic deployments from GitHub
- ✅ Environment management (staging, production)
- ✅ Observability (logs, metrics)
- ✅ Private networking

**Required Secrets:**
- `RAILWAY_TOKEN` - Account settings → Tokens
- `RAILWAY_SERVICE` - Service ID from dashboard

**Database Connection:**
```bash
# Railway provides DATABASE_URL automatically
DATABASE_URL=postgresql://user:pass@host:port/db
```

---

## Fly.io

**Best for:** Global deployment, Docker containers, low latency

**Setup:**
```bash
# Install CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

**Dockerfile Required:**
Fly.io uses your Dockerfile. See [docker-setup.md](docker-setup.md) for examples.

**Configuration:** `fly.toml`
```toml
app = "my-app"
primary_region = "iad"

[http_service]
  internal_port = 3000
  force_https = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Features:**
- ✅ Deploy containers anywhere in the world
- ✅ Auto-scaling
- ✅ Built-in Postgres (flyctl postgres create)
- ✅ Private networking (WireGuard)
- ✅ Health checks

**Required Secrets:**
- `FLY_API_TOKEN` - Dashboard → Account → Access Tokens

---

## AWS (ECS/Fargate)

**Best for:** Enterprise apps, full control, complex architecture

**Setup Steps:**
1. Create ECR repository for Docker images
2. Create ECS cluster
3. Define task definition
4. Create ECS service
5. Configure load balancer (optional)

**Deploy Workflow:**
1. Build Docker image
2. Push to ECR
3. Update ECS service with new image

**See:** [github-actions.md](github-actions.md#aws-ecs-deployment) for complete CI/CD workflow.

**Required Secrets:**
- `AWS_ACCESS_KEY_ID` - IAM user access key
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key
- `ECR_REPOSITORY` - ECR repository URI
- Cluster/service names

**IAM Permissions Needed:**
- ECR: Push/pull images
- ECS: Update services, describe tasks
- CloudWatch: Write logs

**Costs:** Complex pricing based on:
- Compute (Fargate vCPU/memory)
- Data transfer
- Load balancer (if used)
- CloudWatch logs

---

## Custom VPS

**Best for:** Full control, Claude Code development environment, dual-device workflow, persistent sessions

**Overview:**
Deploy your own Virtual Private Server for maximum flexibility. Perfect for:
- Running Claude Code remotely (access from anywhere)
- Long-running tasks with persistent sessions (tmux)
- Multi-device access (Mac, mobile via Termius, Cursor Remote-SSH)
- Working without VPN (if server located outside restricted regions)

**Key Features:**
- ✅ Complete environment control (Ubuntu, dependencies, tools)
- ✅ Persistent sessions survive disconnects (tmux)
- ✅ Access from multiple devices simultaneously
- ✅ SSH key authentication for security
- ✅ Git synchronization between local and remote
- ✅ Cursor IDE Remote-SSH support

**Setup Overview:**
1. Purchase VPS (recommended: 4 CPU, 8GB RAM)
2. Configure SSH access and security
3. Install Node.js, Claude Code, dependencies
4. Set up tmux for persistent sessions
5. Configure Git and GitHub access
6. Set up mobile access (Termius)

**Access Methods:**
- **Terminal (Mac):** SSH with custom aliases (`vps`, `vps-claude`)
- **Cursor IDE:** Remote-SSH extension (full GUI development)
- **Mobile:** Termius app (iOS/Android) with persistent tmux

**Complete Setup Guide:**
See [vps-setup.md](../../methodology/guides/vps-setup.md) for detailed instructions covering:
- Server configuration and security
- SSH key setup for multiple devices
- Claude Code authentication
- tmux configuration
- Dual environment workflow (Mac + VPS)
- Troubleshooting and backup strategies

**Typical Costs:**
- $5-15/month depending on specs and provider
- One-time setup: ~2-3 hours

---

## Chrome Web Store

**Best for:** Browser extensions

**Setup:**
1. Build extension: `npm run build`
2. Create ZIP: `zip -r extension.zip dist/`
3. Upload to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
4. Fill store listing (description, icons, screenshots)
5. Submit for review

**Automated Releases:**
See [github-actions.md](github-actions.md#chrome-extension-release) for GitHub Actions workflow that creates releases on tags.

**Publishing Checklist:**
- [ ] Manifest.json properly configured
- [ ] Icons (16x16, 48x48, 128x128)
- [ ] Screenshots (1280x800 or 640x400)
- [ ] Privacy policy (if collecting data)
- [ ] Store description

**One-time Fee:** $5 developer registration

---

## NPM Registry

**Best for:** Node.js packages, libraries, CLI tools

**Setup:**
```bash
# Login
npm login

# Publish
npm publish
```

**package.json Requirements:**
```json
{
  "name": "my-package",
  "version": "1.0.0",
  "description": "Package description",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "publishConfig": {
    "access": "public"
  }
}
```

**Automated Publishing:**
See [github-actions.md](github-actions.md#npm-package-publishing) for CI/CD workflow.

**Versioning:**
```bash
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0
npm version major  # 1.0.0 → 2.0.0
git push --tags
```

**Required Secret:**
- `NPM_TOKEN` - npmjs.com account settings → Access Tokens

---

## General Deployment Checklist

Before deploying to any platform:

- [ ] Environment variables documented in `deployment.md`
- [ ] Secrets configured in platform dashboard
- [ ] CI/CD pipeline tested
- [ ] Health check endpoint (if applicable)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Logging configured
- [ ] Database migrations strategy (if applicable)
- [ ] Rollback plan documented

---

## Cost Optimization

**Vercel:**
- Use ISR instead of SSR where possible
- Optimize images with next/image
- Monitor function execution time

**Railway:**
- Use sleep mode for dev environments
- Right-size database (start small)
- Use connection pooling

**Fly.io:**
- Start with shared CPU
- Scale regions based on actual traffic
- Use fly-replay for multi-region

**AWS:**
- Use Fargate Spot for non-critical workloads
- Right-size tasks (don't over-provision)
- Use CloudWatch to monitor costs
- Consider Reserved Instances for stable workloads

---

## Monitoring & Observability

**Vercel:** Built-in analytics + Vercel Speed Insights

**Railway:** Built-in metrics dashboard + logs

**Fly.io:** Prometheus metrics + flyctl logs

**AWS:** CloudWatch Logs + CloudWatch Metrics + X-Ray tracing

**Third-party (all platforms):**
- Sentry (error tracking)
- DataDog (APM)
- New Relic (full observability)
- LogRocket (session replay)
