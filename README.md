# � Book Data Pipeline

A fully automated book data pipeline using **Apache Airflow** or **Prefect**, integrated with APIs (NYT, OpenLibrary, Google Books), and storing results in **PostgreSQL**.

---

## � Features
✅ Automated ETL Pipeline  
✅ API Data Extraction (NYT, OpenLibrary, Google Books)  
✅ Data Validation & Quality Checks  
✅ Docker Support for Easy Deployment  
✅ Scalable & Maintainable DAG/Flow Structure  

---

## ⚙️ Project Structure

book_data_pipeline/ │── dags/ # Airflow DAGs │ ├── book_pipeline.py # Main ETL Pipeline │ ├── data/ # Stores temporary data (ignored in Git) │── logs/ # Logs directory (ignored in Git) │── plugins/ # Custom operators & hooks │── Dockerfile # Docker setup │── docker-compose.yml # Compose setup for Airflow │── requirements.txt # Python dependencies │── README.md # Project documentation │── .gitignore # Ignored files


2️⃣ Set Up a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
� Running with Docker
1️⃣ Build and Start Docker Containers
bash
Copy
Edit
docker-compose up --build -d
2️⃣ Check Running Containers
bash
Copy
Edit
docker ps
3️⃣ Access the Airflow Web UI
URL: http://localhost:8080
Default Credentials:
Username: airflow
Password: airflow
� Environment Variables
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
� Running the Pipeline
Trigger DAG from the Airflow UI or manually run:

bash
Copy
Edit
airflow dags trigger book_pipeline
� Checking Database for Data
Run the following queries in PostgreSQL to validate the data:

sql
Copy
Edit
SELECT * FROM books LIMIT 10;
SELECT COUNT(*) FROM books WHERE title IS NULL;
� Logs & Debugging
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
� Contributing
Fork the repository
Create a feature branch
Commit changes
Push and create a pull request
