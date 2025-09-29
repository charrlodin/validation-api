# Testing Examples

## Quick Start

1. **Start the API server:**
```bash
./run.sh
# Or manually:
# source venv/bin/activate
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Open a new terminal and run tests:**

## Basic curl Examples

### Health Check
```bash
curl http://localhost:8000/
```

### Check API Status
```bash
curl http://localhost:8000/status | jq
```

### Validate Single Email & IP
```bash
# Disposable email example
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@mailinator.com",
    "ip": "8.8.8.8"
  }' | jq

# Clean email example
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "ip": "1.1.1.1"
  }' | jq

# IPv6 example
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@guerrillamail.com",
    "ip": "2001:4860:4860::8888"
  }' | jq
```

### Invalid Input Examples
```bash
# Invalid email format
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "ip": "8.8.8.8"
  }' | jq

# Invalid IP address
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "ip": "999.999.999.999"
  }' | jq
```

### Bulk Validation (CSV)
```bash
# Create test CSV file
cat > test.csv << 'EOF'
email,ip
test@mailinator.com,192.0.2.1
user@gmail.com,8.8.8.8
admin@guerrillamail.com,1.2.3.4
contact@10minutemail.com,93.184.216.34
EOF

# Upload and validate
curl -X POST http://localhost:8000/bulk-validate \
  -F "file=@test.csv" \
  -o results.csv

# View results
cat results.csv
```

### Bulk Validation (JSON)
```bash
# Create test JSON file
cat > test.json << 'EOF'
[
  {"email": "test@mailinator.com", "ip": "192.0.2.1"},
  {"email": "user@gmail.com", "ip": "8.8.8.8"},
  {"email": "admin@guerrillamail.com", "ip": "1.2.3.4"}
]
EOF

# Upload and validate
curl -X POST http://localhost:8000/bulk-validate \
  -F "file=@test.json" \
  -o results.csv

# View results
cat results.csv
```

### Manual List Sync
```bash
curl -X POST http://localhost:8000/sync | jq
```

## Python Test Script

Run the comprehensive test suite:
```bash
# In a new terminal (while server is running)
python3 test_api.py
```

## Performance Testing

Test response time:
```bash
time curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "ip": "8.8.8.8"
  }' -s -o /dev/null
```

Run multiple requests:
```bash
for i in {1..10}; do
  time curl -X POST http://localhost:8000/validate \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "ip": "8.8.8.8"}' \
    -s -o /dev/null
done
```

## Common Disposable Email Domains to Test

- mailinator.com
- guerrillamail.com
- 10minutemail.com
- tempmail.com
- throwaway.email
- maildrop.cc
- trashmail.com
- yopmail.com

## Interactive API Documentation

Visit these URLs while the server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Example Response

```json
{
  "email_disposable": true,
  "email_reason": "Domain 'mailinator.com' is in disposable email list",
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "blacklist_last_updated": {
    "ipsum": "2024-01-15T10:30:05Z",
    "bruteforceblocker": "2024-01-15T10:30:12Z"
  }
}
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
```

### Lists not downloading
```bash
# Check if server can reach GitHub
curl -I https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf

# Manually trigger sync
curl -X POST http://localhost:8000/sync
```

### Slow responses
```bash
# Check list sizes
curl http://localhost:8000/status | jq '.email_domains_count, .ip_blacklists'

# Monitor response times
curl -w "\nTime: %{time_total}s\n" -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "ip": "8.8.8.8"}'
```
