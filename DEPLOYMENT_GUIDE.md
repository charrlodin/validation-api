# Deployment Guide - Render

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- Git installed locally

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already)
```bash
cd /Users/arronchild/Projects/validation-api

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Email & IP Validation API

Features:
- Email disposable detection (4,700+ domains)
- IP blacklist checking (188,000+ IPs)
- Risk scoring (0-100)
- Role-based email detection
- Typo suggestions
- IPv6 support
- Rate limiting
- Bulk validation
- Metrics endpoint

Performance:
- p95 latency: 1.5ms
- Tested and production-ready

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"
```

### 1.2 Create GitHub Repository

**Option A: Via GitHub CLI (if installed)**
```bash
# Create repository
gh repo create validation-api --public --source=. --remote=origin

# Push code
git push -u origin main
```

**Option B: Via GitHub Website**
1. Go to https://github.com/new
2. Name: `validation-api`
3. Make it **Public** (or Private if you prefer)
4. Don't initialize with README (we already have files)
5. Click "Create repository"

Then push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/validation-api.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Render

### 2.1 Via Render Dashboard (Easiest)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up or log in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your `validation-api` repository

3. **Configure Service**
   ```
   Name: validation-api
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: (leave blank)
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Plan**
   - **Free tier**: Good for testing
   - **Starter ($7/mo)**: Recommended for production
     - Better performance
     - No sleep on inactivity
     - More resources

5. **Environment Variables** (optional)
   - `PYTHON_VERSION`: 3.11.0

6. **Click "Create Web Service"**

Render will:
- Clone your repository
- Install dependencies
- Start your API
- Provide a public URL (e.g., `https://validation-api.onrender.com`)

### 2.2 Via Render Blueprint (render.yaml)

Your repo already includes `render.yaml`. Just:

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render auto-detects the `render.yaml`
5. Click "Apply"

---

## Step 3: Verify Deployment

### 3.1 Wait for Build
- Build typically takes 2-3 minutes
- Watch the logs in Render dashboard
- Look for "Application startup complete"

### 3.2 Test Your API

Your API will be at: `https://validation-api.onrender.com` (or your custom name)

**Health Check:**
```bash
curl https://validation-api.onrender.com/
```

**Validate Email:**
```bash
curl -X POST https://validation-api.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mailinator.com","ip":"8.8.8.8"}' | python3 -m json.tool
```

**Check Status:**
```bash
curl https://validation-api.onrender.com/status | python3 -m json.tool
```

**View Metrics:**
```bash
curl https://validation-api.onrender.com/metrics | python3 -m json.tool
```

---

## Step 4: Configure Custom Domain (Optional)

### 4.1 Add Custom Domain
1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Click "Add Custom Domain"
4. Enter your domain (e.g., `api.yourdomain.com`)

### 4.2 Update DNS
Add CNAME record:
```
Type: CNAME
Name: api (or your subdomain)
Value: validation-api.onrender.com
TTL: 3600
```

Render automatically provisions SSL certificate.

---

## Step 5: Monitor Your API

### 5.1 Render Dashboard
- **Metrics**: CPU, memory, bandwidth
- **Logs**: Real-time application logs
- **Deploys**: Deploy history
- **Events**: Service events

### 5.2 Built-in Monitoring
Your API includes `/metrics` endpoint:
```bash
curl https://validation-api.onrender.com/metrics
```

Shows:
- Request count
- Error rate
- Latency percentiles (p50, p95, p99)
- Uptime

---

## Configuration Options

### Environment Variables

Add in Render dashboard → Settings → Environment:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PYTHON_VERSION` | Python version | 3.11.0 |
| `SYNC_INTERVAL_HOURS` | List update frequency | 24 |

### Scaling

**Manual Scaling:**
1. Go to Settings → Scaling
2. Choose instance type
3. Set number of instances

**Auto-Scaling** (Starter plan+):
1. Enable auto-scaling
2. Set min/max instances
3. Configure scaling rules

---

## Troubleshooting

### Build Fails

**Check Build Logs:**
1. Go to your service in Render
2. Click on the failing deploy
3. Review build logs

**Common Issues:**
- Python version mismatch → Set `PYTHON_VERSION` env var
- Missing dependencies → Check `requirements.txt`
- Port issues → Ensure using `$PORT` environment variable

**Fix and Redeploy:**
```bash
# Make changes locally
git add .
git commit -m "Fix: deployment issue"
git push origin main
```

Render auto-deploys on push.

### API Not Responding

**Check Logs:**
1. Render Dashboard → Your Service
2. Click "Logs" tab
3. Look for errors

**Common Issues:**
- Lists not syncing → Check network/GitHub access
- Memory limits → Upgrade plan
- Rate limiting → Check metrics

**Manual Restart:**
- Render Dashboard → Service → "Manual Deploy" → "Deploy latest commit"

### Slow First Request

**Issue:** Render free tier sleeps after inactivity

**Solutions:**
1. **Upgrade to Starter plan** ($7/mo) - No sleep
2. **Keep-alive service** - Ping your API every 10 minutes
3. **Accept cold starts** - First request after sleep ~30s

---

## Performance Optimization

### 1. Use Starter Plan or Higher
- No sleep on inactivity
- Better CPU/memory
- Faster response times

### 2. Enable HTTP/2
- Automatically enabled by Render
- Improves performance

### 3. Monitor Metrics
```bash
# Check current performance
curl https://validation-api.onrender.com/metrics

# Watch for:
# - High error rates
# - Slow latencies
# - Memory issues
```

### 4. Scale Horizontally
- Add more instances for high traffic
- Render load balances automatically

---

## Costs

### Free Tier
- **Cost**: $0
- **Limitations**:
  - Sleeps after 15 min inactivity
  - 750 hours/month free
  - Shared CPU/memory
  - Good for testing

### Starter Plan
- **Cost**: $7/month
- **Benefits**:
  - No sleep
  - Dedicated CPU/memory
  - Better performance
  - Recommended for production

### Standard Plan
- **Cost**: $25/month
- **Benefits**:
  - More resources
  - Better for high traffic
  - Advanced features

---

## Continuous Deployment

### Automatic Deploys

Every `git push` to main triggers:
1. Pull latest code
2. Run build command
3. Start application
4. Zero-downtime deployment

### Manual Deploys

Via Render Dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select "Deploy latest commit" or specific commit

### Deploy Hooks

Create webhook for external triggers:
1. Settings → Deploy Hook
2. Copy webhook URL
3. Use in CI/CD or manually:
```bash
curl -X POST https://api.render.com/deploy/srv-xxxxx
```

---

## Security Best Practices

### 1. Environment Variables
- Store secrets in Render environment variables
- Never commit API keys to Git

### 2. Rate Limiting
- Already configured (60/min, 10/min bulk)
- Monitor for abuse in metrics

### 3. HTTPS Only
- Render provides free SSL
- All traffic encrypted

### 4. Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install -U package-name

# Commit and push
git add requirements.txt
git commit -m "chore: update dependencies"
git push
```

---

## Next Steps After Deployment

### 1. Test Thoroughly
```bash
# Run comprehensive tests against production
BASE_URL=https://validation-api.onrender.com python3 comprehensive_test.py
```

### 2. Set Up Monitoring
- Configure uptime monitoring (UptimeRobot, Pingdom)
- Set up error alerting
- Monitor `/metrics` endpoint

### 3. List on RapidAPI
1. Get your production URL
2. Create RapidAPI account
3. Add your API
4. Publish listing

### 4. Documentation
Update your API documentation with:
- Production URL
- Rate limits
- Example requests
- Support information

---

## Support

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### API Support
- GitHub Issues: Your repository
- Email: Your support email
- Documentation: README.md, EXAMPLES.md

---

## Rollback

If deployment fails:

**Via Dashboard:**
1. Go to Deploys tab
2. Find last working deploy
3. Click "Rollback to this version"

**Via Git:**
```bash
# Revert last commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard <commit-hash>
git push origin main --force
```

---

## Summary

✅ **Deployment is easy:**
1. Push code to GitHub
2. Connect to Render
3. Auto-deploy on every push

✅ **Your API includes:**
- Fast performance (1.5ms p95)
- Rate limiting
- Metrics endpoint
- Comprehensive testing
- Complete documentation

✅ **Ready for production!**

---

## Quick Reference

**Your API endpoints after deployment:**
```
https://validation-api.onrender.com/
https://validation-api.onrender.com/status
https://validation-api.onrender.com/validate
https://validation-api.onrender.com/bulk-validate
https://validation-api.onrender.com/metrics
https://validation-api.onrender.com/docs
```

**Deployment commands:**
```bash
# Push to deploy
git push origin main

# Check status
curl https://validation-api.onrender.com/status

# View logs
# Via Render Dashboard → Logs

# Rollback
# Via Render Dashboard → Deploys → Rollback
```

🎉 **You're ready to deploy!**
