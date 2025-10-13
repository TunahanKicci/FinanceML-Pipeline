# CI/CD Pipeline Documentation

## 🚀 Workflows

### 1️⃣ **CI - Test & Lint** (`ci.yml`)
**Trigger:** Push to `main` or `develop`, Pull Requests

**Jobs:**
- ✅ Python linting (flake8)
- ✅ Code formatting check (black)
- ✅ Unit tests (pytest)
- ✅ Security scan (Trivy)
- ✅ Code coverage upload

**Badges:**
```markdown
![CI Status](https://github.com/TunahanKicci/FinanceML-Pipeline/workflows/CI%20-%20Test%20%26%20Lint/badge.svg)
```

---

### 2️⃣ **Docker Build & Push** (`docker-build.yml`)
**Trigger:** Push to `main`, Tags (`v*`), Manual

**Jobs:**
- 🐳 Build API Docker image
- 🐳 Build Frontend Docker image
- 📦 Push to GitHub Container Registry (ghcr.io)
- 🏷️ Tag with version, branch, SHA

**Image URLs:**
- API: `ghcr.io/tunahankicci/financeml-pipeline-api:latest`
- Frontend: `ghcr.io/tunahankicci/financeml-pipeline-frontend:latest`

**Badges:**
```markdown
![Docker Build](https://github.com/TunahanKicci/FinanceML-Pipeline/workflows/Docker%20Build%20%26%20Push/badge.svg)
```

---

### 3️⃣ **Dependency Update Check** (`dependency-check.yml`)
**Trigger:** Weekly (Mondays 9 AM UTC), Manual

**Jobs:**
- 🔍 Check for security vulnerabilities (pip-audit)
- 📊 Generate audit report
- 🚨 Create GitHub issue if vulnerabilities found

---

### 4️⃣ **Update Data Cache** (`cache-update.yml`)
**Trigger:** Daily (6 PM UTC), Manual

**Jobs:**
- 📊 Fetch latest market data from Yahoo Finance
- 💾 Update CSV cache files
- 📤 Commit and push changes automatically
- 📝 Generate update summary

**Note:** This runs the `update_cache.py` script automatically every day after market close.

---

### 5️⃣ **Deploy to Production** (`deploy.yml`)
**Trigger:** Release published, Manual

**Jobs:**
- 🚀 Pull latest Docker images
- 🔄 Update containers
- ✅ Health check
- 🔙 Rollback on failure

**Environments:** `production`, `staging`

---

## 🔧 Setup Instructions

### 1. **GitHub Secrets** (Required)

Navigate to: `Settings → Secrets and variables → Actions`

**For Docker Registry:**
- ✅ `GITHUB_TOKEN` - Auto-provided by GitHub

**For Deployment (Optional):**
- `DEPLOY_HOST` - Server IP/hostname
- `DEPLOY_USER` - SSH username
- `DEPLOY_KEY` - SSH private key
- `DEPLOY_PORT` - SSH port (default: 22)
- `DEPLOY_URL` - Application URL for health check

### 2. **Enable GitHub Actions**

1. Go to repository `Settings → Actions → General`
2. Select: **Allow all actions and reusable workflows**
3. Workflow permissions: **Read and write permissions**
4. Check: **Allow GitHub Actions to create and approve pull requests**

### 3. **Enable Container Registry**

1. Go to repository `Settings → Packages`
2. Make package public (if needed)
3. Link repository to package

---

## 📊 Workflow Triggers

| Workflow | Push | PR | Schedule | Manual |
|----------|------|-------|----------|--------|
| CI | ✅ | ✅ | ❌ | ❌ |
| Docker Build | ✅ (main) | ❌ | ❌ | ✅ |
| Dependency Check | ❌ | ❌ | ✅ Weekly | ✅ |
| Cache Update | ❌ | ❌ | ✅ Daily | ✅ |
| Deploy | ❌ | ❌ | ❌ | ✅ |

---

## 🎯 Best Practices

### **Branching Strategy:**
```
main (production)
  ↑
develop (staging)
  ↑
feature/* (development)
```

### **Versioning:**
- Use semantic versioning: `v1.0.0`, `v1.1.0`, etc.
- Create tags for releases
- Docker images tagged with version + `latest`

### **Testing:**
- All PRs must pass CI checks
- Minimum code coverage: 70% (when tests added)
- Security scans must pass

---

## 🚀 Manual Workflow Runs

### **Trigger Docker Build:**
```bash
# Via GitHub UI
Actions → Docker Build & Push → Run workflow

# Via GitHub CLI
gh workflow run docker-build.yml
```

### **Trigger Cache Update:**
```bash
gh workflow run cache-update.yml
```

### **Deploy to Production:**
```bash
gh workflow run deploy.yml -f environment=production
```

---

## 📈 Monitoring

### **View Workflow Runs:**
```
Repository → Actions → Select workflow
```

### **Check Docker Images:**
```
Repository → Packages
```

### **View Logs:**
```
Actions → Workflow run → Job → Step logs
```

---

## 🛠️ Local Testing

### **Test CI locally with act:**
```bash
# Install act: https://github.com/nektos/act
act -j test

# Test specific workflow
act -W .github/workflows/ci.yml
```

### **Test Docker build:**
```bash
docker compose build --no-cache
docker compose up -d
```

---

## 🔄 Continuous Improvement

### **Planned Enhancements:**
- [ ] Add integration tests
- [ ] Implement E2E tests with Playwright
- [ ] Add performance benchmarking
- [ ] Implement canary deployments
- [ ] Add Slack/Discord notifications
- [ ] Implement automatic rollback on errors
- [ ] Add ML model retraining workflow

---

## 📞 Support

For CI/CD issues:
1. Check workflow logs in Actions tab
2. Review GitHub Actions status page
3. Contact repository maintainers

**Last Updated:** October 13, 2025
