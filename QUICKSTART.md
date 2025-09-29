# Quick Start Guide

## Try the Live API

**Production URL:** https://validation-api-zgxh.onrender.com

### 1. Health Check

```bash
curl https://validation-api-zgxh.onrender.com/
```

### 2. Validate an Email

```bash
curl -X POST https://validation-api-zgxh.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mailinator.com","ip":"8.8.8.8"}'
```

### 3. Check API Status

```bash
curl https://validation-api-zgxh.onrender.com/status
```

### 4. View Interactive Docs

Visit: https://validation-api-zgxh.onrender.com/docs

## Response Format

```json
{
  "email_disposable": true,
  "email_reason": "Domain 'mailinator.com' is in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": null,
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 70
}
```

## Risk Scoring

- **0-20**: Low risk (clean)
- **21-50**: Medium risk (role-based)
- **51-80**: High risk (disposable or blacklisted)
- **81-100**: Critical risk (multiple factors)

## Self-Hosting

```bash
git clone https://github.com/charrlodin/validation-api.git
cd validation-api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for details.

## Rate Limits

- `/validate`: 60 requests/minute
- `/bulk-validate`: 10 requests/minute

## Need Help?

- 📚 [Full Documentation](README.md)
- 🔧 [API Reference](https://validation-api-zgxh.onrender.com/docs)
- 💬 [GitHub Issues](https://github.com/charrlodin/validation-api/issues)
