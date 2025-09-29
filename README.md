# Email & IP Validation API

A high-performance REST API for validating email addresses and IP addresses against public blocklists.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://validation-api-zgxh.onrender.com/docs)
[![API Status](https://img.shields.io/badge/status-production-blue)](https://validation-api-zgxh.onrender.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- ⚡ **Fast**: <10ms API processing time
- 📧 **Email Validation**: 4,700+ disposable email domains
- 🌐 **IP Blacklist**: 188,000+ malicious IPs
- 🎯 **Risk Scoring**: 0-100 risk assessment
- 🔍 **Smart Detection**: Role-based emails, typo suggestions
- 🌍 **IPv6 Support**: Both IPv4 and IPv6
- 🔄 **Auto-Update**: Daily sync with latest data
- 📊 **Metrics**: Performance tracking built-in

## Quick Start

### Try It Live

**Production API:** https://validation-api-zgxh.onrender.com

**Interactive Docs:** https://validation-api-zgxh.onrender.com/docs

### Example Request

```bash
curl -X POST https://validation-api-zgxh.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mailinator.com","ip":"8.8.8.8"}'
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
  "risk_score": 70,
  "blacklist_last_updated": {
    "ipsum": "2025-09-29T20:57:15Z",
    "bruteforceblocker": "2025-09-29T20:57:16Z"
  }
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/status` | GET | Data source statistics |
| `/metrics` | GET | Performance metrics |
| `/validate` | POST | Validate single email & IP |
| `/bulk-validate` | POST | Batch validation (CSV/JSON) |
| `/docs` | GET | Interactive API documentation |

## Use Cases

- 🛡️ **Fraud Prevention**: Block disposable emails and suspicious IPs
- 📝 **User Registration**: Validate signups in real-time
- 📧 **Email Marketing**: Clean your email lists
- 🔒 **Security**: Detect malicious traffic
- 📊 **Data Quality**: Maintain clean databases

## Self-Hosting

Want to run your own instance? Clone and deploy:

```bash
git clone https://github.com/charrlodin/validation-api.git
cd validation-api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## Data Sources

All data is sourced from public, open-source lists:

- **Disposable Emails**: [disposable-email-domains](https://github.com/disposable-email-domains/disposable-email-domains) (CC0 License)
- **IP Blacklist**: [IPsum](https://github.com/stamparm/ipsum) (Unlicense)
- **Brute Force IPs**: [BruteForceBlocker](https://danger.rulez.sk/projects/bruteforceblocker/)

Lists are automatically synced every 24 hours.

## Technology Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Validation**: Pydantic v2
- **Rate Limiting**: SlowAPI
- **Scheduler**: APScheduler
- **Deployment**: Render

## Performance

- **Processing Time**: <1ms (internal)
- **Response Time**: ~300ms (including network)
- **Uptime**: 99.9%
- **Rate Limit**: 60 requests/minute

## API Options

### 🆓 Self-Hosted (GitHub)
Clone this repo and deploy yourself:
- ✅ Free and open source
- ✅ Full control
- ✅ Customize as needed
- ⚠️ You manage infrastructure
- ⚠️ You handle updates

### 💼 Managed Service (RapidAPI)
Use our hosted API on RapidAPI:
- ✅ No deployment needed
- ✅ Automatic updates
- ✅ Guaranteed uptime
- ✅ Professional support
- ✅ Pay-as-you-go

[View on RapidAPI →](#) *(Coming soon)*

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 2 minutes
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Self-hosting guide
- [UPDATES.md](UPDATES.md) - Changelog

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

**TL;DR:** Free to use, modify, and distribute. Commercial use allowed.

## Support

- 📧 Issues: [GitHub Issues](https://github.com/charrlodin/validation-api/issues)
- 📚 Docs: [API Documentation](https://validation-api-zgxh.onrender.com/docs)
- 🌐 Website: [validation-api-zgxh.onrender.com](https://validation-api-zgxh.onrender.com)

## Acknowledgments

Thanks to the maintainers of the public data sources that make this API possible.

---

**Made with ❤️ by [charrlodin](https://github.com/charrlodin)**

**⭐ Star this repo if you find it useful!**
