# FutureBot - Quick Start

## 🚀 In 5 Minuten lauffähig

### 1. Prerequis ites
- Python 3.11+ installiert
- Bybit Testnet Account (https://testnet.bybit.com/)
- Terminal/Command Line

### 2. Setup Backend

```bash
# In FutureBot Verzeichnis
cd backend

# Automatisches Setup
./setup.sh

# Falls setup.sh nicht ausführbar:
chmod +x setup.sh && ./setup.sh
```

### 3. Konfiguration

Editiere `backend/.env`:

```bash
# Minimum Configuration
BYBIT_API_KEY=dein_testnet_api_key
BYBIT_API_SECRET=dein_testnet_secret
SECRET_KEY=eine-lange-zufaellige-zeichenfolge-min-32-zeichen

# Paper Trading aktiviert (Standard)
ENABLE_PAPER_TRADING=true
BYBIT_TESTNET=true
```

**Wichtig**: SECRET_KEY muss mindestens 32 Zeichen lang sein!

```bash
# Generiere einen sicheren Secret Key:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Starte den Server

```bash
cd backend
source venv/bin/activate  # Virtual environment aktivieren
uvicorn app.main:app --reload
```

Server läuft auf: **http://localhost:8000**

### 5. Teste die API

#### Browser
- API Dokumentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

#### Terminal
```bash
# Health Check
curl http://localhost:8000/health

# Portfolio Stats
curl http://localhost:8000/api/v1/portfolio/stats

# Ticker abrufen
curl http://localhost:8000/api/v1/market-data/ticker/BTCUSDT
```

#### Beispiel: Order erstellen

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "buy",
    "order_type": "market",
    "quantity": "0.001"
  }'
```

## 📊 Verfügbare API Endpoints

### Orders
- `POST /api/v1/orders` - Neue Order erstellen
- `GET /api/v1/orders` - Alle Orders abrufen
- `GET /api/v1/orders/{id}` - Spezifische Order
- `DELETE /api/v1/orders/{id}` - Order stornieren

### Positions
- `GET /api/v1/positions` - Offene Positionen
- `GET /api/v1/positions/{id}` - Spezifische Position
- `POST /api/v1/positions/{id}/close` - Position schließen

### Portfolio
- `GET /api/v1/portfolio/stats` - Portfolio Statistiken

### Market Data
- `GET /api/v1/market-data/ticker/{symbol}` - Ticker Daten
- `GET /api/v1/market-data/kline/{symbol}` - Candlestick Daten

## 🧪 Tests ausführen

```bash
cd backend
source venv/bin/activate

# Alle Tests
pytest tests/ -v

# Mit Coverage
pytest --cov=app tests/

# Nur Unit Tests
pytest tests/unit/ -v
```

## 📝 Projekt-Struktur

```
backend/
├── app/
│   ├── main.py              # FastAPI Entry Point
│   ├── core/                # Config, Logging, DB
│   ├── models/              # Database Models
│   ├── schemas/             # API Schemas
│   ├── services/            # Business Logic
│   ├── repositories/        # Data Access
│   └── api/v1/endpoints/    # API Routes
├── tests/                   # Tests
└── logs/                    # Log Files
```

## 🔍 Entwicklungs-Workflow

### Live Logs ansehen
```bash
tail -f backend/logs/futurebot.log
```

### Code formatieren
```bash
cd backend
source venv/bin/activate
black app/
```

### Type Checking
```bash
mypy app/
```

## ⚙️ Wichtige Einstellungen (.env)

```bash
# Trading
MAX_POSITION_SIZE_USD=1000        # Max Position in USD
MAX_LEVERAGE=10                   # Max Hebel
RISK_PER_TRADE=0.02              # 2% Risiko pro Trade
MAX_OPEN_POSITIONS=3             # Max gleichzeitige Positionen

# Risk Management
MAX_DAILY_DRAWDOWN=0.05          # 5% max täglicher Verlust
STOP_LOSS_PERCENTAGE=0.02        # 2% Stop Loss
TAKE_PROFIT_PERCENTAGE=0.04      # 4% Take Profit

# Features
ENABLE_PAPER_TRADING=true        # Paper Trading Modus
ENABLE_AUTO_TRADING=false        # Auto-Trading (VORSICHT!)
ENABLE_ML_PREDICTIONS=false      # ML aktivieren
```

## 🚨 Häufige Probleme

### "Module not found" Fehler
```bash
# Stelle sicher, dass Virtual Environment aktiv ist
source backend/venv/bin/activate

# Dependencies neu installieren
pip install -r backend/requirements.txt
```

### "Invalid API key" Fehler
1. Prüfe ob API Keys korrekt in `.env` eingetragen sind
2. Keine Leerzeichen um das `=` Zeichen
3. `BYBIT_TESTNET=true` wenn du Testnet-Keys nutzt

### "SECRET_KEY too short" Fehler
```bash
# Generiere neuen Key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Kopiere Output in .env als SECRET_KEY
```

### Server startet nicht
```bash
# Port 8000 bereits belegt?
lsof -ti:8000 | xargs kill -9

# Oder anderen Port nutzen:
uvicorn app.main:app --reload --port 8001
```

## 📖 Nächste Schritte

1. **Paper Trading testen**: Erstelle Orders über die API
2. **Portfolio ansehen**: Checke `/api/v1/portfolio/stats`
3. **Logs überprüfen**: `tail -f backend/logs/futurebot.log`
4. **Dokumentation lesen**: `docs/GETTING_STARTED.md`

## 🔐 Sicherheit

✅ **DO**:
- Testnet für Experimente nutzen
- API Keys sicher aufbewahren
- `.env` niemals committen
- Paper Trading zuerst testen

❌ **DON'T**:
- Mainnet ohne ausgiebiges Testing
- API Keys teilen oder committen
- Auto-Trading ohne Überwachung
- Alle Einstellungen auf Maximum

## 💡 Tipps

- **API Docs nutzen**: http://localhost:8000/docs ist interaktiv!
- **Logs sind dein Freund**: Immer `logs/futurebot.log` checken
- **Klein starten**: Erst mit kleinen Beträgen testen
- **Strategien testen**: Backtesting vor Live-Trading

---

**Viel Erfolg! 🎯**

Bei Fragen: Siehe `docs/` Ordner oder README.md
