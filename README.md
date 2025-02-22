# í³š Book Data Pipeline

A fully automated book data pipeline using **Apache Airflow** or **Prefect**, integrated with APIs (NYT, OpenLibrary, Google Books), and storing results in **PostgreSQL**.

---

## í³Œ Features
âœ… Automated ETL Pipeline  
âœ… API Data Extraction (NYT, OpenLibrary, Google Books)  
âœ… Data Validation & Quality Checks  
âœ… Docker Support for Easy Deployment  
âœ… Scalable & Maintainable DAG/Flow Structure  

---

## âš™ï¸ Project Structure

book_data_pipeline/ â”‚â”€â”€ dags/ # Airflow DAGs â”‚ â”œâ”€â”€ book_pipeline.py # Main ETL Pipeline â”‚ â”œâ”€â”€ data/ # Stores temporary data (ignored in Git) â”‚â”€â”€ logs/ # Logs directory (ignored in Git) â”‚â”€â”€ plugins/ # Custom operators & hooks â”‚â”€â”€ Dockerfile # Docker setup â”‚â”€â”€ docker-compose.yml # Compose setup for Airflow â”‚â”€â”€ requirements.txt # Python dependencies â”‚â”€â”€ README.md # Project documentation â”‚â”€â”€ .gitignore # Ignored files


2ï¸âƒ£ Set Up a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
í°³ Running with Docker
1ï¸âƒ£ Build and Start Docker Containers
bash
Copy
Edit
docker-compose up --build -d
2ï¸âƒ£ Check Running Containers
bash
Copy
Edit
docker ps
3ï¸âƒ£ Access the Airflow Web UI
URL: http://localhost:8080
Default Credentials:
Username: airflow
Password: airflow
í³‚ Environment Variables
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
íº€ Running the Pipeline
Trigger DAG from the Airflow UI or manually run:

bash
Copy
Edit
airflow dags trigger book_pipeline
í³Š Checking Database for Data
Run the following queries in PostgreSQL to validate the data:

sql
Copy
Edit
SELECT * FROM books LIMIT 10;
SELECT COUNT(*) FROM books WHERE title IS NULL;
í³œ Logs & Debugging
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
í´ Contributing
Fork the repository
Create a feature branch
Commit changes
Push and create a pull request
