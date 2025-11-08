# Getting Started with FutureBot

## Quick Start (5 Minuten)

### 1. Backend Setup

```bash
cd backend

# Automatisches Setup
./setup.sh

# Oder manuell:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Konfiguration

Editiere `backend/.env`:

```bash
# Wichtig: Trage deine Bybit API Credentials ein
BYBIT_API_KEY=dein_api_key
BYBIT_API_SECRET=dein_api_secret
BYBIT_TESTNET=true  # Für erste Tests!

# Optional: Andere Einstellungen anpassen
MAX_POSITION_SIZE_USD=1000
RISK_PER_TRADE=0.02
```

### 3. Starte den Backend-Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Server läuft auf: http://localhost:8000

- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 4. Teste die API

```bash
# Health Check
curl http://localhost:8000/health

# Root Endpoint
curl http://localhost:8000/
```

## Bybit API Keys erstellen

### Testnet (Empfohlen für Start)

1. Gehe zu https://testnet.bybit.com/
2. Registriere einen Account
3. Erhalte kostenloses Test-USDT (10.000$)
4. API Management → Create New Key
   - **Permissions**: Read & Write für Contract Trading
   - **IP Restriction**: Deaktiviert (für lokale Tests)
5. Speichere Key & Secret in `.env`

### Mainnet (Nur für Production!)

⚠️ **Vorsicht**: Echtes Geld! Erst nach ausgiebigem Testing!

1. https://www.bybit.com/
2. Account erstellen & verifizieren
3. API Management → Create New Key
   - **Permissions**: Minimal (nur was benötigt wird)
   - **IP Restriction**: Aktiviert (Sicherheit!)
   - **2FA**: Aktiviert

## Projektstruktur verstehen

```
backend/
├── app/
│   ├── main.py              # FastAPI Entry Point
│   ├── core/                # Core-Funktionalität
│   │   ├── config.py        # Alle Einstellungen
│   │   ├── logging.py       # Strukturiertes Logging
│   │   └── database.py      # DB Connection
│   ├── models/              # SQLAlchemy Models
│   │   ├── order.py         # Order-Datenbank-Model
│   │   └── position.py      # Position-Datenbank-Model
│   ├── schemas/             # Pydantic Schemas (API)
│   │   └── order.py         # API Request/Response
│   ├── services/            # Business Logic
│   │   └── bybit_client.py  # Bybit API Wrapper
│   └── api/                 # API Endpoints (kommt später)
├── tests/                   # Tests
├── logs/                    # Log-Dateien
└── .env                     # Deine Konfiguration
```

## Nächste Schritte

### Phase 1: Daten sammeln (Aktuell)
- ✅ Bybit API Client implementiert
- ⏳ Market Data Service
- ⏳ Daten in Datenbank speichern
- ⏳ Echtzeit-Updates via WebSocket

### Phase 2: Paper Trading
- ⏳ Simulations-Engine
- ⏳ Order Execution (Papier)
- ⏳ Portfolio Tracking
- ⏳ Performance Analytics

### Phase 3: Strategien
- ⏳ Base Strategy Interface
- ⏳ Simple Moving Average Strategy
- ⏳ Backtesting Framework
- ⏳ Parameter Optimization

### Phase 4: Web Interface
- ⏳ React Frontend
- ⏳ Dashboard
- ⏳ Order Management UI
- ⏳ Live Charts

### Phase 5: Machine Learning
- ⏳ Feature Engineering
- ⏳ LSTM Preisvorhersage
- ⏳ RL für Strategy Optimization

## Häufige Probleme

### "Module not found"
```bash
# Stelle sicher, dass du im venv bist
source venv/bin/activate

# Reinstalliere dependencies
pip install -r requirements.txt
```

### "Database error"
```bash
# Lösche alte DB und erstelle neu
rm futurebot.db
# Backend neu starten
```

### "Bybit API error: Invalid API key"
```bash
# Prüfe .env Datei
cat .env | grep BYBIT

# Stelle sicher:
# 1. Keine Leerzeichen um =
# 2. API Key korrekt kopiert
# 3. Testnet=true wenn Testnet-Keys
```

### "TA-Lib installation failed"
```bash
# macOS (M1/M2):
brew install ta-lib
pip install ta-lib

# Oder ohne TA-Lib (optional):
# Entferne ta-lib aus requirements.txt
```

## Development Workflow

### 1. Feature entwickeln
```bash
git checkout -b feature/mein-feature
# Code schreiben...
```

### 2. Tests ausführen
```bash
pytest tests/ -v
pytest --cov=app  # Mit Coverage
```

### 3. Code Quality
```bash
# Format code
black app/

# Linting
ruff check app/

# Type checking
mypy app/
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: mein neues feature"
git push origin feature/mein-feature
```

## Monitoring

### Logs ansehen
```bash
# Live logs
tail -f logs/futurebot.log

# Strukturierte Logs filtern (JSON in production)
cat logs/futurebot.log | grep ERROR
```

### Performance
```bash
# Später: Prometheus Metrics
# http://localhost:8000/metrics
```

## Support

- 📚 Dokumentation: `/docs` Ordner
- 🐛 Issues: GitHub Issues
- 💬 Fragen: Diskussionen mit Team

## Sicherheit

⚠️ **WICHTIG**:
- ❌ Niemals API Keys committen
- ❌ Niemals echtes Geld ohne Tests
- ✅ Immer Testnet zuerst
- ✅ `.env` in `.gitignore`
- ✅ IP Whitelisting in Production
- ✅ 2FA aktiviert

---

**Happy Trading! 🚀**
