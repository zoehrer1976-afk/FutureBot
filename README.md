# FutureBot - AI-Powered Crypto Trading Bot

Modularer, KI-basierter Trading-Bot für Kryptomärkte mit Fokus auf Skalierbarkeit und Wartbarkeit.

## 🏗️ Architektur-Übersicht

```
FutureBot/
├── backend/                    # Python Backend (FastAPI)
│   ├── app/
│   │   ├── api/               # API Layer
│   │   │   └── v1/
│   │   │       ├── endpoints/ # Route Handler (max 200 Zeilen)
│   │   │       └── dependencies/ # FastAPI Dependencies
│   │   ├── core/              # Core Funktionalität
│   │   │   ├── config.py      # Konfiguration
│   │   │   ├── logging.py     # Logging Setup
│   │   │   ├── database.py    # DB Connection
│   │   │   └── security.py    # Auth & Security
│   │   ├── models/            # SQLAlchemy Models
│   │   ├── schemas/           # Pydantic Schemas (API)
│   │   ├── services/          # Business Logic Layer
│   │   │   ├── trading_service.py
│   │   │   ├── data_service.py
│   │   │   └── risk_service.py
│   │   ├── repositories/      # Data Access Layer
│   │   │   ├── order_repository.py
│   │   │   └── market_data_repository.py
│   │   ├── strategies/        # Trading Strategies
│   │   │   ├── base_strategy.py
│   │   │   └── implementations/
│   │   ├── ml/                # Machine Learning
│   │   │   ├── models/        # ML Model Definitionen
│   │   │   ├── training/      # Training Pipeline
│   │   │   └── inference/     # Prediction Service
│   │   └── utils/             # Helper Funktionen
│   ├── tests/                 # Tests
│   │   ├── unit/
│   │   └── integration/
│   └── migrations/            # Alembic Migrations
│
├── frontend/                   # React Frontend
│   └── src/
│       ├── components/        # React Components
│       │   ├── common/        # Wiederverwendbare Components
│       │   ├── dashboard/     # Dashboard-spezifisch
│       │   ├── orders/        # Order Management
│       │   ├── strategies/    # Strategy Configuration
│       │   └── settings/      # Einstellungen
│       ├── hooks/             # Custom React Hooks
│       ├── services/          # API Client
│       ├── contexts/          # React Context (State)
│       └── utils/             # Helper Functions
│
├── data/                      # Daten (nicht versioniert)
│   ├── raw/                   # Rohdaten von APIs
│   └── processed/             # Feature-engineered Daten
│
├── models/                    # Trainierte ML-Models (nicht versioniert)
├── logs/                      # Application Logs
├── config/                    # Konfigurationsdateien
├── docs/                      # Dokumentation
└── scripts/                   # Utility Scripts

```

## 🎯 Design-Prinzipien

### 1. **Modularität**
- Jede Datei: **max 300 Zeilen**
- Jede Funktion: **max 50 Zeilen**
- Single Responsibility Principle

### 2. **Layered Architecture**
```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← HTTP Requests
├─────────────────────────────────────┤
│      Service Layer (Business)       │  ← Orchestrierung
├─────────────────────────────────────┤
│   Repository Layer (Data Access)    │  ← DB Zugriff
├─────────────────────────────────────┤
│        Models (SQLAlchemy)          │  ← Datenstrukturen
└─────────────────────────────────────┘
```

### 3. **Dependency Injection**
- Lose Kopplung zwischen Komponenten
- Einfaches Testing durch Mock-Injection
- Konfigurierbar über FastAPI `Depends()`

### 4. **Factory Pattern**
- `StrategyFactory`: Erzeugt Trading-Strategien
- `ModelFactory`: Lädt ML-Modelle
- `ExecutorFactory`: Erstellt Order-Executors

## 📦 Module-Übersicht

### Backend Core Module

#### **1. Data Ingestion** (`services/data_service.py`)
- Bybit API Integration
- Historische & Echtzeit-Daten
- Feature Engineering
- Daten-Validierung

#### **2. Trading Service** (`services/trading_service.py`)
- Order-Platzierung (Live & Paper)
- Position Management
- Stop-Loss / Take-Profit
- Portfolio-Verwaltung

#### **3. Risk Management** (`services/risk_service.py`)
- Position-Sizing
- Drawdown Limits
- Liquidation-Schutz
- Circuit Breaker

#### **4. Strategy Engine** (`strategies/`)
- Base Strategy Interface
- Regelbasierte Strategien
- ML-basierte Strategien
- Backtesting-Unterstützung

#### **5. ML Pipeline** (`ml/`)
- Model Training
- Feature Store
- Model Registry
- Inference Service

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (für Frontend)
- Bybit API Key (Testnet empfohlen)

### Installation

```bash
# 1. Clone Repository
git clone <repo-url>
cd FutureBot

# 2. Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 3. Environment Variables
cp .env.example .env
# Editiere .env mit deinen Bybit API Keys

# 4. Database Initialisierung
alembic upgrade head

# 5. Backend starten
uvicorn app.main:app --reload

# 6. Frontend Setup (neues Terminal)
cd ../frontend
npm install
npm start
```

## 🔧 Konfiguration

### Environment Variables (`.env`)
```bash
# API Keys
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
BYBIT_TESTNET=true

# Database
DATABASE_URL=sqlite:///./futurebot.db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Trading
MAX_POSITION_SIZE=1000
MAX_LEVERAGE=10
RISK_PER_TRADE=0.02
```

## 📊 API Endpoints

### Trading
- `POST /api/v1/orders` - Place Order
- `GET /api/v1/orders` - List Orders
- `DELETE /api/v1/orders/{id}` - Cancel Order
- `GET /api/v1/positions` - Active Positions

### Data
- `GET /api/v1/market-data/{symbol}` - Market Data
- `GET /api/v1/indicators/{symbol}` - Technical Indicators

### Strategies
- `GET /api/v1/strategies` - List Strategies
- `POST /api/v1/strategies/{id}/activate` - Activate Strategy
- `POST /api/v1/backtest` - Run Backtest

## 🧪 Testing

```bash
# Unit Tests
pytest tests/unit -v

# Integration Tests
pytest tests/integration -v

# Coverage Report
pytest --cov=app --cov-report=html
```

## 📝 Development Workflow

1. **Feature Branch erstellen**: `git checkout -b feature/your-feature`
2. **Code schreiben** (max 300 Zeilen/Datei!)
3. **Tests hinzufügen**
4. **Commit**: `git commit -m "feat: your feature"`
5. **Push**: `git push origin feature/your-feature`

## 🔒 Security

- ✅ API Keys in Environment Variables
- ✅ Input Validation (Pydantic)
- ✅ Rate Limiting
- ✅ SQL Injection Prevention (SQLAlchemy)
- ✅ CORS Configuration
- ⚠️ **Niemals** Testnet-Keys für Production!

## 📚 Weitere Dokumentation

- [Architektur Details](docs/architecture.md)
- [API Dokumentation](http://localhost:8000/docs)
- [Trading Strategies](docs/strategies.md)
- [ML Pipeline](docs/ml-pipeline.md)

## ⚠️ Disclaimer

Dieses Projekt dient zu Lern- und Forschungszwecken. Trading mit Kryptowährungen birgt erhebliche Risiken. Nutze immer das Testnet für Experimente!

## 📄 License

MIT
