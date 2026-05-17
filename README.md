Global Intelligence Data Pipeline
A full-stack, containerized data pipeline that automatically aggregates global news and search trends. The backend is built with FastAPI, handling everything from data ingestion and cleaning with Pandas to user registration and secure token authentication, all backed by a PostgreSQL database.

Note: This project is currently in the pre-deployment phase and runs entirely in a local containerized environment via Docker Compose.

Features
Automated Data Ingestion:

Google Trends Tracker: Uses pytrends to fetch search interest metrics over the past 12 months for custom keywords. It uses custom browser headers to handle data extraction reliably.

Global News Aggregator: Connects to a live News API, extracting specific categories (technology, world, crime) while handling edge cases like duplicate removal and timezone cleaning.

Secure API & User Authentication:

Features a built-in user system that allows new accounts to register with secure, hashed passwords (bcrypt).

Uses JSON Web Tokens (JWT) for secure logins. This means endpoints like /news and /trends are locked down and can only be viewed by authenticated users holding a valid security token.

Background Task Engine:

Uses FastAPI’s native background tasks to run the scraping pipeline. When a system task triggers a crawl, the API immediately responds with an Accepted status so the system doesn't freeze or time out while processing data.

Containerized Environment:

Runs inside a multi-container Docker setup. The Python API application and the PostgreSQL database run as separate, isolated services that securely communicate inside their own private network layer.

Tech Stack
Backend & API Layer: Python, FastAPI, Uvicorn

Data Processing & Analytics: Pandas, SQLAlchemy (PostgreSQL engine wrapper)

Security & Auth: JWT tokens (python-jose), Passlib (bcrypt password hashing)

Database & Infrastructure: PostgreSQL, Docker, Docker Compose

Project Structure
google.py & news_api.py - Custom scripts responsible for fetching, cleaning, and formatting data from external sources.

main.py - The central orchestrator that triggers both scripts and updates the database tables using Pandas.

api.py - The FastAPI server handling user accounts, JWT authentication, data delivery routes, and automated backend execution endpoints.

Dockerfile & docker-compose.yml - Infrastructure specifications that configure the virtual application and database containers.