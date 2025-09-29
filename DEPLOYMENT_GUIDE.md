# Deployment Guide

## Quick Deploy to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- Git repository

---

## Step 1: Deploy to Render

### Via Render Dashboard

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up or log in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your repository

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

5. **Click "Create Web Service"**

Render will:
- Clone your repository
- Install dependencies
- Start your API
- Provide a public URL

### Via Render Blueprint (render.yaml)

Your repo includes `render.yaml`:

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render auto-detects the `render.yaml`
5. Click "Apply"

---

## Step 2: Verify Deployment

### Test Your API

```bash
# Health Check
curl https://your-api.onrender.com/

# Validate Email
curl -X POST https://your-api.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mailinator.com","ip":"8.8.8.8"}'

# Check Status
curl https://your-api.onrender.com/status

# View Metrics
curl https://your-api.onrender.com/metrics
```

---

## Configuration

### Environment Variables

Add in Render dashboard → Settings → Environment:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PYTHON_VERSION` | Python version | 3.11.0 |
| `SYNC_INTERVAL_HOURS` | List update frequency | 24 |

### Scaling

**Manual Scaling:**
1. Settings → Scaling
2. Choose instance type
3. Set number of instances

**Auto-Scaling** (Starter plan+):
1. Enable auto-scaling
2. Set min/max instances
3. Configure scaling rules

---

## Custom Domain (Optional)

### Add Custom Domain
1. Render dashboard → Your service → Settings
2. Click "Custom Domains"
3. Add your domain (e.g., `api.yourdomain.com`)

### Update DNS
Add CNAME record:
```
Type: CNAME
Name: api
Value: your-service.onrender.com
TTL: 3600
```

Render automatically provisions SSL certificate.

---

## Monitoring

### Render Dashboard
- **Metrics**: CPU, memory, bandwidth
- **Logs**: Real-time logs
- **Deploys**: Deploy history

### Built-in Metrics
Your API includes `/metrics` endpoint:
```bash
curl https://your-api.onrender.com/metrics
```

Shows:
- Request count
- Error rate
- Latency percentiles
- Uptime

---

## Troubleshooting

### Build Fails

1. Check build logs in Render dashboard
2. Review error messages
3. Common issues:
   - Python version mismatch → Set `PYTHON_VERSION` env var
   - Missing dependencies → Check `requirements.txt`
   - Port issues → Ensure using `$PORT` variable

### API Not Responding

1. Check logs in Render dashboard
2. Verify lists synced successfully
3. Manual restart: Dashboard → Manual Deploy

### Slow First Request

**Free tier sleeps after inactivity**

Solutions:
1. Upgrade to Starter plan ($7/mo) - No sleep
2. Accept cold starts (~30s first request)

---

## Performance

### Optimization Tips

1. **Use Starter Plan or Higher**
   - No sleep
   - Better performance
   - Dedicated resources

2. **Monitor Metrics**
   ```bash
   curl https://your-api.onrender.com/metrics
   ```

3. **Scale Horizontally**
   - Add instances for high traffic
   - Auto load balancing

---

## Continuous Deployment

### Automatic Deploys

Every `git push` to main triggers:
1. Pull latest code
2. Build
3. Deploy with zero downtime

### Manual Deploy

Via Render Dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select commit

---

## Pricing

### Free Tier
- $0/month
- Sleeps after 15 min inactivity
- 750 hours/month
- Good for testing

### Starter Plan
- $7/month
- No sleep
- Dedicated resources
- Recommended for production

### Standard Plan
- $25/month
- More resources
- High traffic

---

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Render Status**: https://status.render.com

---

## Quick Reference

**Deployment:**
```bash
git push origin main  # Auto-deploys
```

**Testing:**
```bash
curl https://your-api.onrender.com/
curl https://your-api.onrender.com/status
curl https://your-api.onrender.com/metrics
```

**Rollback:**
- Via Render Dashboard → Deploys → Rollback

---

🎉 **Ready to deploy!**
