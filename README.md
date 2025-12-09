# 📦 Catalog Service — FastAPI + Cloud Run + Cloud SQL

Deployed on Cloud Run: **https://catalog-1003140017553.us-east1.run.app/docs**

A production-ready microservice for managing catalog items and item images.  
Fully built with **FastAPI**, **SQLAlchemy ORM**, and deployed using **Google Cloud Run** with a **Cloud SQL (MySQL)** backend.

---

## 🚀 Features

### ✅ Item Management
- Create / Retrieve / Update / Delete items  
- Filter by category, price range, and status  
- Pagination support (`limit`, `offset`)  
- Automatic ID assignment  

### 🖼 Item Image Management
- Attach images to items  
- Update image details  
- Retrieve image sets  
- Delete images  

### 🧩 API Documentation
- Interactive Swagger UI → `/docs`
- OpenAPI schema → `/openapi.json`

### 🛡 Stability & Validation
- Pydantic models  
- Error handling  
- Health check endpoint (`/health`)

---

## 🧱 Tech Stack

| Component | Technology |
|----------|------------|
| API Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | MySQL (Cloud SQL) |
| Deployment | Google Cloud Run |
| Build | Cloud Build |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
catalog-service/
│
├── main.py                 # FastAPI app, DB engine, routes
├── models/
│   ├── item.py             # Item schemas & validation
│   └── item_image.py       # Image schemas
│
├── sql/
│   ├── items.sql           # Table DDL
│   └── item_images.sql     # Table DDL
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Environment Variables

The service loads DB configuration from:

```
DATABASE_URL
```

### Local Development (SQLite fallback)

If `DATABASE_URL` is not set, the app automatically uses:

```
sqlite:///./catalog.db
```

### Cloud Run + Cloud SQL (MySQL)

Example:

```
mysql+pymysql://root:PASSWORD@/Catalog_db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
```

---

## 🧪 Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
uvicorn main:app --reload
```

### 3. Open:
- Local API → http://127.0.0.1:8000  
- Swagger UI → http://127.0.0.1:8000/docs  
- ReDoc → http://127.0.0.1:8000/redoc

---

## ☁️ Deploying to Cloud Run

### 1. Push code to GitHub  
Cloud Build automatically triggers and builds the container.

### 2. Configure Cloud Run
- Set **container image URL** to the built Artifact Registry image  
- Attach Cloud SQL instance  
- Add environment variable:

```
DATABASE_URL = mysql+pymysql://root:PASSWORD@/Catalog_db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
```

### 3. Deploy

Cloud Run will run the container and expose your API securely.

---

## 🧪 Example API Usage

### Create an Item
```bash
curl -X POST "https://<CLOUD_RUN_URL>/items" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Golf Club",
        "description": "Driver",
        "price": 199.99,
        "status": "ACTIVE"
      }'
```

### Get Items
```bash
curl "https://<CLOUD_RUN_URL>/items?limit=50&offset=0"
```

---

## 👤 Author
**Can Yang**  
FastAPI Developer | Cloud Run | SQL | Python  
