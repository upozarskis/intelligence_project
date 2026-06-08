# Intelligence Data Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_EC2-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AWS_RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)

A full-stack, containerized data engineering pipeline that autonomously aggregates, processes, and serves global technology and cybersecurity intelligence using a **Medallion Architecture (Bronze-Silver-Gold)**.

This system extracts real-time search trends and global news, transforms the data using Pandas, and loads it into a secure AWS RDS database. The backend is powered by a FastAPI REST application featuring secure JWT authentication and background task orchestration, fully deployed on an AWS EC2 instance.

---

## Dashboard Preview

<img width="522" height="402" alt="login" src="https://github.com/user-attachments/assets/838dd45e-ab0a-4130-ba03-ab05cd597a45" />
<img width="1200" height="450" alt="latest_news" src="https://github.com/user-attachments/assets/dfeb2106-4a91-4765-b984-362e86e39a63" />
<img width="1200" height="450" alt="google_trends" src="https://github.com/user-attachments/assets/f869b29d-4c2b-479f-b2b9-636040653bfb" />

---

##  Medallion Architecture
The system processes data through three distinct quality tiers to ensure reliability and scalability:
* **Bronze (Raw):** Stores landing-zone data exactly as retrieved from sources (Trends & News API) to maintain a full historical audit trail.
* **Silver (Standardized):** Cleans, deduplicates, and standardizes schemas across disparate sources, creating a "trusted" dataset.
* **Gold (Curated):** Aggregates business-ready insights, pre-calculated metrics, and topic-specific matrices optimized for high-performance dashboarding.

##  Key Features
* **Automated Pipeline:** Orchestrated via Linux cron, the system executes the full Medallion workflow daily, transforming raw data into business intelligence.
* **Secure RESTful API:** FastAPI-powered endpoints with JWT authentication and bcrypt password hashing.
* **Asynchronous Orchestration:** Utilizes FastAPI background tasks for non-blocking data ingestion, ensuring seamless user experience during heavy processing.
* **Cloud-Native:** Fully containerized with Docker, deployed on AWS EC2, and utilizing AWS RDS (PostgreSQL) for storage.

---

## Tech Stack

| Category | Technologies Used |
| :--- | :--- |
| **Backend API** | Python, FastAPI, Uvicorn |
| **Data Engineering** | Pandas, Pytrends, SQLAlchemy, Medallion Patterns |
| **Database** | PostgreSQL, AWS RDS | 
| **Security** | JWT (python-jose), Passlib (bcrypt) |
| **DevOps & Cloud** | Docker, Docker Compose, Linux (Ubuntu), AWS EC2, AWS RDS, Cron, Nginx |

---

## Project Structure

```text
├── main.py                 # Pipeline Orchestrator (Triggers the ETL workflow)
├── api.py                  # FastAPI server: Handles Auth & Data Serving
├── pipeline/               # Core Data Engineering Logic
│   ├── extract.py           # EXTRACTION: Fetches raw data from Trends & News APIs
│   ├── transform.py           # TRANSFORMATION: Cleans, deduplicates, and standardizes
│   └── gold.py             # AGGREGATION: Generates business insights & matrices
├── docker-compose.yml      # Infrastructure & network isolation
├── Dockerfile              # Container environment configuration
└── requirements.txt        # Dependencies
```
