# HNG_Stage_One_String_Analyzer

HNG Stage One String Analyzer repo

# HNG Backend Wizards — Stage 1 Task

## 📍 Description

A RESTful API service that analyzes strings and stores their computed properties including:

* Length of the string
* Palindrome check
* Word count
* Unique characters
* SHA-256 hash
* Character frequency map

The API supports creating, retrieving, deleting strings, and filtering using natural language queries.

---

## 🚀 Technologies

* Python 3.x
* Django
* Django REST Framework
* psycopg2-binary (PostgreSQL adapter)
* python-dotenv

---

## Project Structure

```
HNG_Stage_One_String_Analyzer/
│
├── analyzer/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 Features

* **POST** `/strings/` → Analyze and store a new string
* **GET** `/strings/<string_value>/` → Retrieve a specific string
* **DELETE** `/strings/<string_value>/` → Delete a specific string
* **GET** `/strings/filter-by-natural-language?query=...` → Filter strings using natural language
* All responses include computed properties and timestamps in ISO 8601 format
* Fully built using Django REST Framework with APIView

---

## 🤠 Example JSON Response for POST `/strings/`

```json
{
  "id": "e1cbb0c3879af8347246f12c559a86b1b9e5c8c2d6c6f1f7d3cfa9a4c2f04df1",
  "value": "racecar",
  "properties": {
    "length": 7,
    "is_palindrome": true,
    "unique_characters": 4,
    "word_count": 1,
    "sha256_hash": "e1cbb0c3879af8347246f12c559a86b1b9e5c8c2d6c6f1f7d3cfa9a4c2f04df1",
    "character_frequency_map": {
      "r": 2,
      "a": 2,
      "c": 2,
      "e": 1
    }
  },
  "created_at": "2025-10-20T21:00:00Z"
}
```

---

# 🔧 Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/HNG_Stage_One_String_Analyzer.git
cd HNG_Stage_One_String_Analyzer
```

### 2️⃣ Create a Python virtual environment

```bash
python -m venv venv
```

### 3️⃣ Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4️⃣ Install dependencies

```bash
pip install Django==5.1.1 djangorestframework==3.15.2 psycopg2-binary==2.9.10 python-dotenv==1.0.0
```

### 5️⃣ Configure environment variables

Create a `.env` file in the project root with the following content:

```bash
USE_SQLITE=False
DB_NAME=string_analyzer_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-hng-stage1-string-analyzer
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 6️⃣ Ensure PostgreSQL is running (Linux)

```bash
sudo service postgresql start
```

### 7️⃣ Create the PostgreSQL database (if it doesn't exist)

```bash
sudo -u postgres psql -c "CREATE DATABASE string_analyzer_db;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'your_postgres_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE string_analyzer_db TO postgres;"
```

### 8️⃣ Apply Django migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 9️⃣ Run the development server

```bash
python manage.py runserver
```

The API is now available at: `http://127.0.0.1:8000/api/`

---

## 👤 Author

**Full Name:** Abraham Franklin Okumbor
**Email:** [okumborfranklin@gmail.com](mailto:okumborfranklin@gmail.com)
**Stack:** Python / Django / Django REST Framework

```}
```
