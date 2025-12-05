# Phishing Detection API

Backend API untuk deteksi URL phishing menggunakan machine learning Random Forest.

## Features

- 🔍 **URL Analysis**: Analisis URL untuk mendeteksi phishing dengan confidence score
- 🌐 **Network Information**: Deteksi redirect chain, IP address, dan geolocation
- 📊 **Detailed Features**: Ekstraksi 22+ fitur dari URL dan konten web
- 📚 **Educational Content**: Informasi tentang jenis-jenis phishing dan strategi mitigasi
- 🌍 **Multi-language**: Dukungan Bahasa Indonesia dan English
- 📈 **Statistics**: Tracking statistik analisis dalam session
- 🔒 **CORS Support**: Siap diintegrasikan dengan frontend Next.js

## Tech Stack

- **Framework**: FastAPI 0.104+
- **ML**: scikit-learn, Random Forest Classifier
- **Feature Extraction**: BeautifulSoup4, Requests
- **Validation**: Pydantic v2

## Installation

### Prerequisites

- Python 3.10+
- Model file: `random_forest_model.pkl` (harus ada di root directory)

### Setup

1. Clone repository dan masuk ke direktori:

```bash
cd phising-detection-api
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy dan configure environment variables:

```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

5. Pastikan model file ada:

```bash
# Model harus ada di: ../random_forest_model.pkl
# Atau sesuaikan MODEL_PATH di .env
```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
docker-compose up -d
```

## API Documentation

Setelah aplikasi berjalan, akses dokumentasi interaktif di:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Detection

#### POST `/api/v1/predict`

Analisis URL untuk deteksi phishing.

**Request Body:**

```json
{
  "url": "https://example.com"
}
```

**Response:**

```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "confidence": 0.95,
  "risk_level": "low",
  "risk_indicators": [],
  "features": {
    "url_similarity_index": 100.0,
    "char_continuation_rate": 0.15,
    "tld": "com",
    "no_of_dot_in_url": 2,
    "no_of_dash_in_url": 0,
    "url_is_live": 1,
    "has_title": 1,
    "has_favicon": 1,
    "has_social_net": 1,
    "has_copyright_info": 1,
    "no_of_js": 5
  },
  "network_info": {
    "redirect_chain": [],
    "final_url": "https://example.com",
    "ip_address": "93.184.216.34",
    "location": {
      "country": "United States",
      "city": "Los Angeles",
      "region": "California"
    }
  },
  "detection_timestamp": "2024-12-05T10:30:00Z",
  "analysis_time_ms": 245
}
```

### Health & Statistics

#### GET `/api/v1/health`

Check service health dan model status.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "timestamp": "2024-12-05T10:30:00Z"
}
```

#### GET `/api/v1/stats`

Get analysis statistics untuk session saat ini.

**Response:**

```json
{
  "total_analyzed": 150,
  "phishing_detected": 45,
  "legitimate_detected": 105,
  "avg_confidence": 0.87,
  "session_start": "2024-12-05T09:00:00Z"
}
```

### Information

#### GET `/api/v1/info/phishing?lang=en`

Get informasi edukatif tentang phishing.

**Query Parameters:**

- `lang`: Language code (`en` atau `id`)

**Response:**

```json
{
  "categories": [
    {
      "type": "Email Phishing",
      "description": "...",
      "indicators": [...],
      "examples": [...]
    }
  ],
  "language": "en"
}
```

#### GET `/api/v1/info/mitigation?lang=en`

Get strategi mitigasi phishing.

**Query Parameters:**

- `lang`: Language code (`en` atau `id`)

**Response:**

```json
{
  "individual": [...],
  "organization": [...],
  "language": "en"
}
```

## Environment Variables

| Variable           | Description                            | Default                      |
| ------------------ | -------------------------------------- | ---------------------------- |
| `MODEL_PATH`       | Path to model file                     | `../random_forest_model.pkl` |
| `HOST`             | Server host                            | `0.0.0.0`                    |
| `PORT`             | Server port                            | `8000`                       |
| `ALLOWED_ORIGINS`  | CORS allowed origins (comma-separated) | `http://localhost:3000`      |
| `SCRAPING_TIMEOUT` | Timeout for web scraping (seconds)     | `5`                          |
| `MAX_REDIRECTS`    | Maximum redirects to follow            | `10`                         |
| `LOG_LEVEL`        | Logging level                          | `INFO`                       |
| `LOG_FORMAT`       | Log format (`json` or `text`)          | `json`                       |

## Project Structure

```
phising-detection-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── detection.py    # Detection endpoint
│   │       ├── health.py       # Health & stats endpoints
│   │       └── info.py         # Information endpoints
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── logging.py         # Logging setup
│   ├── data/
│   │   ├── phishing_info.json # Phishing information
│   │   └── mitigation_info.json # Mitigation strategies
│   ├── ml/
│   │   ├── model_loader.py    # Model loading
│   │   └── predictor.py       # Prediction logic
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── feature_extractor.py # Feature extraction
│   │   ├── tld_encoder.py      # TLD encoding
│   │   ├── url_analyzer.py     # URL analysis orchestration
│   │   └── stats_service.py    # Statistics tracking
│   └── main.py                # FastAPI application
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
└── README.md                  # This file
```

## Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Development

### Code Formatting

```bash
black app/
```

### Linting

```bash
flake8 app/
```

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### Manual Deployment

1. Install dependencies
2. Set environment variables
3. Run with production server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Performance Considerations

- **Response Time**: Target < 3 seconds per analysis
- **Scraping Timeout**: 5 seconds default (configurable)
- **Concurrent Requests**: Supports multiple concurrent requests
- **Caching**: Static data (phishing info, mitigation) cached in memory

## Security

- Input validation dengan Pydantic
- URL sanitization
- Rate limiting support
- CORS configuration
- Structured logging untuk audit trail

## License

[Your License Here]

## Support

Untuk pertanyaan atau issues, silakan buat issue di repository ini.
