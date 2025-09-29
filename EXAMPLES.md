# Usage Examples

## Basic Validation

### Disposable Email Detection

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@mailinator.com",
    "ip": "8.8.8.8"
  }'
```

**Response:**
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

### Clean Email

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "ip": "1.1.1.1"
  }'
```

**Response:**
```json
{
  "email_disposable": false,
  "email_reason": "Domain 'gmail.com' is not in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": null,
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 0
}
```

---

## Advanced Features

### Role-Based Email Detection

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "ip": "8.8.8.8"
  }'
```

**Response:**
```json
{
  "email_disposable": false,
  "email_reason": "Domain 'example.com' is not in disposable email list",
  "email_role_based": true,
  "email_typo_suggestion": null,
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 20
}
```

### Typo Detection

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmal.com",
    "ip": "8.8.8.8"
  }'
```

**Response:**
```json
{
  "email_disposable": true,
  "email_reason": "Domain 'gmal.com' is in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": "user@gmail.com",
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 80
}
```

### IPv6 Support

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "ip": "2001:4860:4860::8888"
  }'
```

---

## Bulk Validation

### CSV Upload

Create `emails.csv`:
```csv
email,ip
test@mailinator.com,192.0.2.1
user@gmail.com,8.8.8.8
admin@example.com,1.2.3.4
```

Upload:
```bash
curl -X POST https://your-api-url.onrender.com/bulk-validate \
  -F "file=@emails.csv" \
  -o results.csv
```

### JSON Upload

Create `emails.json`:
```json
[
  {"email": "test@mailinator.com", "ip": "192.0.2.1"},
  {"email": "user@gmail.com", "ip": "8.8.8.8"},
  {"email": "admin@example.com", "ip": "1.2.3.4"}
]
```

Upload:
```bash
curl -X POST https://your-api-url.onrender.com/bulk-validate \
  -F "file=@emails.json" \
  -o results.csv
```

---

## API Information

### Check Status

```bash
curl https://your-api-url.onrender.com/status
```

**Response:**
```json
{
  "status": "ok",
  "email_domains_count": 4727,
  "email_last_updated": "2025-09-29T20:57:09Z",
  "ip_blacklists": {
    "ipsum": 188454,
    "bruteforceblocker": 265
  },
  "ip_last_updated": {
    "ipsum": "2025-09-29T20:57:15Z",
    "bruteforceblocker": "2025-09-29T20:57:16Z"
  }
}
```

### View Metrics

```bash
curl https://your-api-url.onrender.com/metrics
```

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 1250,
  "error_count": 0,
  "error_rate": 0.0,
  "requests_per_second": 0.347,
  "latency_ms": {
    "p50": 0.07,
    "p95": 0.10,
    "p99": 0.15
  }
}
```

### Manual Sync

```bash
curl -X POST https://your-api-url.onrender.com/sync
```

---

## Error Handling

### Invalid Email

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "ip": "8.8.8.8"
  }'
```

**Response (422):**
```json
{
  "detail": [{
    "type": "value_error",
    "loc": ["body", "email"],
    "msg": "Value error, Invalid email format"
  }]
}
```

### Invalid IP

```bash
curl -X POST https://your-api-url.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "ip": "999.999.999.999"
  }'
```

**Response (422):**
```json
{
  "detail": [{
    "type": "value_error",
    "loc": ["body", "ip"],
    "msg": "Value error, Invalid IP address format"
  }]
}
```

---

## Python Example

```python
import requests

API_URL = "https://your-api-url.onrender.com"

def validate_email_ip(email, ip):
    response = requests.post(
        f"{API_URL}/validate",
        json={"email": email, "ip": ip}
    )
    return response.json()

# Test
result = validate_email_ip("test@mailinator.com", "8.8.8.8")
print(f"Disposable: {result['email_disposable']}")
print(f"Risk Score: {result['risk_score']}/100")
```

## JavaScript Example

```javascript
const API_URL = "https://your-api-url.onrender.com";

async function validateEmailIP(email, ip) {
  const response = await fetch(`${API_URL}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, ip })
  });
  return await response.json();
}

// Test
validateEmailIP("test@mailinator.com", "8.8.8.8")
  .then(result => {
    console.log(`Disposable: ${result.email_disposable}`);
    console.log(`Risk Score: ${result.risk_score}/100`);
  });
```

---

## Common Use Cases

### User Registration
```python
def validate_signup(email, ip):
    result = validate_email_ip(email, ip)
    
    if result['risk_score'] > 50:
        return {
            'allowed': False,
            'reason': 'High risk email or IP detected'
        }
    
    return {'allowed': True}
```

### Email List Cleaning
```bash
# Bulk validate entire list
curl -X POST https://your-api-url.onrender.com/bulk-validate \
  -F "file=@email_list.csv" \
  -o cleaned_results.csv

# Filter out disposables
awk -F',' '$3=="False"' cleaned_results.csv > clean_emails.csv
```

### Fraud Detection
```python
def check_fraud_risk(email, ip):
    result = validate_email_ip(email, ip)
    
    risk_level = 'low'
    if result['risk_score'] > 80:
        risk_level = 'critical'
    elif result['risk_score'] > 50:
        risk_level = 'high'
    elif result['risk_score'] > 20:
        risk_level = 'medium'
    
    return {
        'risk_level': risk_level,
        'disposable_email': result['email_disposable'],
        'blacklisted_ip': result['ip_blacklisted'],
        'factors': []
    }
```

---

## Rate Limits

- `/validate`: 60 requests/minute per IP
- `/bulk-validate`: 10 requests/minute per IP

Exceeded limits return HTTP 429 with `Retry-After` header.

---

## Interactive Documentation

Visit `/docs` for interactive API documentation:
```
https://your-api-url.onrender.com/docs
```
