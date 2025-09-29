# Quick Start Guide

## 1. Start the Server

```bash
cd validation-api
./run.sh
```

Wait for the message: "Application startup complete."

## 2. Test in Another Terminal

### Health Check
```bash
curl http://localhost:8000/
```

### Check Status & Statistics
```bash
curl http://localhost:8000/status | python3 -m json.tool
```

### Validate Disposable Email
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@mailinator.com", "ip": "8.8.8.8"}' \
  | python3 -m json.tool
```

Expected: `email_disposable: true`

### Validate Clean Email
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@gmail.com", "ip": "1.1.1.1"}' \
  | python3 -m json.tool
```

Expected: `email_disposable: false`

### Bulk Validate CSV
```bash
curl -X POST http://localhost:8000/bulk-validate \
  -F "file=@test.csv" \
  -o results.csv

cat results.csv
```

## 3. View Interactive Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Disposable Email Domains

Test with these:
- mailinator.com ✓
- guerrillamail.com ✓
- 10minutemail.com ✓
- tempmail.com
- throwaway.email
- maildrop.cc

## Performance

Expected response times:
- `/validate`: <100ms
- Email check: <0.01ms
- IP check: <0.02ms

## Troubleshooting

**Port already in use?**
```bash
lsof -i :8000
kill -9 <PID>
```

**Dependencies issue?**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

- Read `README.md` for complete documentation
- See `EXAMPLES.md` for more testing examples
- Check `SUMMARY.md` for project overview
- Run `python3 test_api.py` for comprehensive tests
