# Global Intelligence Data Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_EC2-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AWS_RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)

A full-stack, containerized data engineering pipeline that autonomously aggregates, processes, and serves global technology and cybersecurity intelligence. 

This system extracts real-time search trends and global news, transforms the data using Pandas, and loads it into a secure AWS RDS database. The backend is powered by a FastAPI REST application featuring secure JWT authentication and background task orchestration, fully deployed on an AWS EC2 instance.

---

## Dashboard Preview

<img width="522" height="402" alt="login" src="https://github.com/user-attachments/assets/838dd45e-ab0a-4130-ba03-ab05cd597a45" />
<img width="1200" height="450" alt="latest_news" src="https://github.com/user-attachments/assets/dfeb2106-4a91-4765-b984-362e86e39a63" />
<img width="1200" height="450" alt="google_trends" src="https://github.com/user-attachments/assets/f869b29d-4c2b-479f-b2b9-636040653bfb" />

---

## Key Architecture & Features

### 1. Automated ETL Pipeline (Extract, Transform, Load)
* **Search Trends Tracker:** Utilizes `pytrends` with custom browser headers to extract 12-month rolling search interest metrics for strategic geopolitical and tech keywords.
* **Global News Aggregator:** Connects to live News APIs, extracting targeted categories (Technology, Cybersecurity, World).
* **Data Transformation:** Leverages **Pandas** to clean data, handle timezones, drop duplicates, and structure schemas before injecting them into the database using SQLAlchemy.
* **Autonomous Execution:** Orchestrated via a Linux `cron` job that silently wakes the pipeline at 2:00 AM server time daily to fetch and archive new data without manual intervention.

### 2. Secure RESTful API
* **JWT Authentication:** Endpoints like `/news` and `/trends` are strictly protected. Users must register and authenticate to receive a JSON Web Token (JWT) for access.
* **Cryptographic Hashing:** User passwords are encrypted using `bcrypt` (Passlib) before touching the database.
* **Asynchronous Processing:** Utilizes FastAPI’s native background tasks. When a system task triggers a massive data crawl, the API immediately returns an HTTP 202 `Accepted` status, ensuring the client never times out while the server processes data.

### 3. Cloud DevOps & Containerization
* **Decoupled Architecture:** The Python API application is fully containerized, isolating the compute layer while securely communicating with a managed AWS RDS database instance over an encrypted cloud network.
* **Production Deployment:** Hosted on **AWS EC2**, utilizing Nginx as a reverse proxy to route public internet traffic securely to the internal Docker containers.

---

## Tech Stack

| Category | Technologies Used |
| :--- | :--- |
| **Backend API** | Python, FastAPI, Uvicorn |
| **Data Engineering** | Pandas, Pytrends, SQLAlchemy |
| **Database** | PostgreSQL, AWS RDS | 
| **Security** | JWT (python-jose), Passlib (bcrypt) |
| **DevOps & Cloud** | Docker, Docker Compose, Linux (Ubuntu), AWS EC2, AWS RDS, Cron, Nginx |

---

## Project Structure

```text
├── main.py                 # Core orchestrator; triggers ETL jobs & updates DB via Pandas
├── api.py                  # FastAPI server: Handles routing, JWT auth, and background tasks
├── google.py               # Custom extraction script for Google Trends data
├── news_api.py             # Custom extraction and cleaning script for global news
├── docker-compose.yml      # Infrastructure config for API and Database network isolation
├── Dockerfile              # Container blueprint for the Python environment
└── requirements.txt        # Python package dependencies
```
