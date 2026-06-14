# Enterprise Salary Insights Dashboard

Backend/Data Engineering pipeline and interactive multi-dimensional analytics dashboard built on a serverless PostgreSQL database layer. Designed with a modern, glassmorphic B2B SaaS aesthetic to provide real-time salary trend telemetry across various demographic and professional vectors.

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%28Neon%29-336791.svg)](https://neon.tech/)
[![ORM/Driver](https://img.shields.io/badge/driver-Psycopg2%20%7C%20SQLAlchemy-2f5f98.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🗺️ System Architecture & Data Flow


```

[ Raw CSV Dataset ] ──( ETL Pipeline / SQLAlchemy )──> [ Neon Serverless PostgreSQL ]
│
(Secure Parameterized SQL & Caching)
▼
[ Live Public Deployment ] <──( Streamlit Cloud ) <─── [ Streamlit / Plotly UI ]

```

1. **Ingestion & ETL Layer**: A standalone Python pipeline reads, cleanses, validates, and bulk-inserts raw structured datasets into an external PostgreSQL cluster via SQLAlchemy chunked transactions.
2. **Database Layer**: Hosted on a serverless, auto-scaling PostgreSQL instance utilizing native relational indexing to handle relational filtering efficiently.
3. **Analytics UI Layer**: Built using Streamlit and Plotly Dark templates, implementing dynamic server-side SQL pooling to prevent memory overhead on the frontend server.

---

## 🛠️ Key Engineering Features

* **Serverless Database Ingestion**: Implements an isolated ETL script (`load_salary_data.py`) featuring structural data cleaning, automated null-value handling, and high-performance `multi`-method bulk insertion with controlled chunk sizes (`chunksize=1000`).
* **Performance Optimization & Caching**: Utilizes Streamlit's operational memory layer via `@st.cache_data` to cache database lookups, minimizing connection handshakes and ensuring sub-second UI rendering upon filter manipulation.
* **Security & SQL Injection Prevention**: Dynamic sidebar filtering relies heavily on parameterized server-side execution (`"Gender" = ANY(%s)`), completely isolating input parameters from the SQL compilation engine.
* **Premium B2B UX Aesthetic**: Transformed the standard layout into a Bento Grid-style dashboard using custom CSS injections to render high-contrast glassmorphic card elements, custom radial background gradients, and hardware-accelerated blur vectors.

---

## 📊 Database Schema

The core analytics layer queries a highly optimized relational table named `salary_data`:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Age` | `DOUBLE PRECISION` | Age of the individual professional |
| `Gender` | `TEXT` | Gender classification for demographic benchmarking |
| `Education Level` | `TEXT` | Academic tier attained (Bachelor's, Master's, PhD) |
| `Job Title` | `TEXT` | Specific industry role/designation |
| `Years of Experience` | `DOUBLE PRECISION` | Total baseline industry domain experience |
| `Salary` | `DOUBLE PRECISION` | Normalized annual compensation metrics |

---

## 🚀 Local Deployment Setup

### 1. Clone the Architecture
```bash
git clone [https://github.com/engrmaziz/salary-trends-dashboard.git](https://github.com/engrmaziz/salary-trends-dashboard.git)
cd salary-trends-dashboard

```

### 2. Configure Environment Secrets

Create a `.env` file within the project root directory (refer to `.env.example`):

```env
DATABASE_URL=postgresql://<user>:<password>@<endpoint>.neon.tech/<dbname>?sslmode=require

```

### 3. Initialize Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

```

### 4. Run the ETL Database Seeder

```bash
python load_salary_data.py

```

### 5. Launch the Enterprise Analytics UI

```bash
streamlit run app.py

```

---

## 📈 Dashboard Telemetry Modules

* **Strategic KPI Grid**: Top-level executive breakdown indicating true data scope, dynamic filtered average base salaries, and maximum scale ceiling indicators.
* **Academic ROIs (Bar Analytics)**: Mean distribution charts sorting educational tiers via compensation weight to determine explicit certification values.
* **Demographic Densities (Donut Analysis)**: Proportional market breakdowns showing exactly how academic representation splits within the target ecosystem.
* **Experience Scalability (Multi-Scatter)**: Granular, multi-variable tracking comparing experiential scaling vectors against actual compensation trends, isolated by demographic lines.

```

```