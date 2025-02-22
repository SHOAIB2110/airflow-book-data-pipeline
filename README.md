# ν³ Book Data Pipeline

A fully automated book data pipeline using **Apache Airflow** or **Prefect**, integrated with APIs (NYT, OpenLibrary, Google Books), and storing results in **PostgreSQL**.

---

## ν³ Features
β Automated ETL Pipeline  
β API Data Extraction (NYT, OpenLibrary, Google Books)  
β Data Validation & Quality Checks  
β Docker Support for Easy Deployment  
β Scalable & Maintainable DAG/Flow Structure  

---

## βοΈ Project Structure

book_data_pipeline/ βββ dags/ # Airflow DAGs β βββ book_pipeline.py # Main ETL Pipeline β βββ data/ # Stores temporary data (ignored in Git) βββ logs/ # Logs directory (ignored in Git) βββ plugins/ # Custom operators & hooks βββ Dockerfile # Docker setup βββ docker-compose.yml # Compose setup for Airflow βββ requirements.txt # Python dependencies βββ README.md # Project documentation βββ .gitignore # Ignored files


2οΈβ£ Set Up a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
ν°³ Running with Docker
1οΈβ£ Build and Start Docker Containers
bash
Copy
Edit
docker-compose up --build -d
2οΈβ£ Check Running Containers
bash
Copy
Edit
docker ps
3οΈβ£ Access the Airflow Web UI
URL: http://localhost:8080
Default Credentials:
Username: airflow
Password: airflow
ν³ Environment Variables
Before running, create a .env file:

bash
Copy
Edit
touch .env
Edit .env:

env
Copy
Edit
AIRFLOW__CORE__EXECUTOR=LocalExecutor
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
API_KEY_NYT=your-nyt-api-key
API_KEY_GOOGLE=your-google-api-key
νΊ Running the Pipeline
Trigger DAG from the Airflow UI or manually run:

bash
Copy
Edit
airflow dags trigger book_pipeline
ν³ Checking Database for Data
Run the following queries in PostgreSQL to validate the data:

sql
Copy
Edit
SELECT * FROM books LIMIT 10;
SELECT COUNT(*) FROM books WHERE title IS NULL;
ν³ Logs & Debugging
Check logs inside Docker:

bash
Copy
Edit
docker logs -f airflow_scheduler
Check task logs:

bash
Copy
Edit
airflow tasks logs book_pipeline extract_books
ν΄ Contributing
Fork the repository
Create a feature branch
Commit changes
Push and create a pull request
