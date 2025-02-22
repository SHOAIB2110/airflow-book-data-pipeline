from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import pandas as pd
import backoff
from sqlalchemy import create_engine, text
import numpy as np
import os

#Retrieve API Keys from Environment Variables
NYT_API_KEY = os.getenv("NYT_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


#Storing API Endpoints
NYT_URL = f"https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key={NYT_API_KEY}"
OPEN_LIBRARY_URL = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json&jscmd=data"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}"


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://airflow:airflow@postgres:5432/airflow")
engine = create_engine(DATABASE_URL)

#Data Directory to store the data 
DATA_DIR = "dags/data"
os.makedirs(DATA_DIR, exist_ok=True)

QUALITY_REPORT_FILE = f"{DATA_DIR}/data_quality_report.txt"

#Function which checks API Retry
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Fetch NYTimes Books Data
def fetch_nytimes_books():
    data = fetch_data(NYT_URL)
    with open(f"{DATA_DIR}/nyt_books.json", "w") as f:
        json.dump(data, f)
    print("NYT data saved successfully!")

# Fetch Open Library Data
def fetch_openlibrary_data():
    with open(f"{DATA_DIR}/nyt_books.json", "r") as f:
        nyt_data = json.load(f)
    isbn_list = [book["primary_isbn13"] for book in nyt_data["results"]["books"]]
    openlibrary_data = {}
    for isbn in isbn_list:
        url = OPEN_LIBRARY_URL.format(isbn)
        try:
            openlibrary_data[isbn] = fetch_data(url)
        except Exception as e:
            print(f"Failed to fetch Open Library data for ISBN {isbn}: {e}")

    with open(f"{DATA_DIR}/openlibrary_data.json", "w") as f:
        json.dump(openlibrary_data, f)
    print("Open Library data saved successfully!")

# Fetch Google Books Data
def fetch_google_books_data():
    with open(f"{DATA_DIR}/nyt_books.json", "r") as f:
        nyt_data = json.load(f)

    isbn_list = [book["primary_isbn13"] for book in nyt_data["results"]["books"]]
    google_books_data = {}
    for isbn in isbn_list:
        url = GOOGLE_BOOKS_URL.format(isbn, GOOGLE_BOOKS_API_KEY)
        try:
            google_books_data[isbn] = fetch_data(url)
        except Exception as e:
            print(f"Failed to fetch Google Books data for ISBN {isbn}: {e}")
    with open(f"{DATA_DIR}/google_books.json", "w") as f:
        json.dump(google_books_data, f)
    print("Google Books data saved successfully!")

def transform_and_enrich_data():
    nyt_file = f"{DATA_DIR}/nyt_books.json"
    openlib_file = f"{DATA_DIR}/openlibrary_data.json"
    google_file = f"{DATA_DIR}/google_books.json"
    output_file = f"{DATA_DIR}/transformed_books.csv"

    # Checking all the files exisit or not
    if not os.path.exists(nyt_file) or not os.path.exists(openlib_file) or not os.path.exists(google_file):
        raise FileNotFoundError("One or more input data files are missing.")

    # Load the source data in file
    with open(nyt_file, "r") as f:
        nyt_data = json.load(f)
    with open(openlib_file, "r") as f:
        openlib_data = json.load(f)
    with open(google_file, "r") as f:
        google_data = json.load(f)
    books = []
    list_name = nyt_data["results"].get("list_name", "Unknown")
    publication_date = nyt_data["results"].get("published_date","")

    for book in nyt_data["results"]["books"]:
        isbn = book["primary_isbn13"]

        # Extracting Open Library Data from JSOn
        openlib_info = openlib_data.get(isbn, {}).get(f"ISBN:{isbn}", {}).get("cover", {})
        cover_image = openlib_info.get("large", None)
        
        # Extracting Google Books Data from json
        google_info = google_data.get(isbn, {}).get("items", [{}])[0].get("volumeInfo", {})
        page_count = google_info.get("pageCount", None)
        language = google_info.get("language", None)
        google_cover = google_info.get("imageLinks", {}).get("thumbnail", None)

        book_entry = {
            "title": book.get("title", "Unknown"),
            "author": book.get("author", "Unknown"),
            "publisher": book.get("publisher", "Unknown"),
            "publication_date": publication_date,
            "ISBN": isbn,
            "description": book.get("description", "Unknown"),
            "rank": book.get("rank", -1),  # Default -1 if missing
            "list_name": list_name,  
            "weeks_on_list": book.get("weeks_on_list", 0),
            "page_count": page_count,
            "language": language,
            "cover_image_url": google_cover,
            "buy_links": ", ".join([link["url"] for link in book.get("buy_links", [])]),
            "data_source": "NYTimes, OpenLibrary, GoogleBooks",
            "ingested_at": datetime.utcnow().isoformat()
        }

        books.append(book_entry)

    df = pd.DataFrame(books)
    df.to_csv(output_file, index=False)
    print(f"Transformed data saved to {output_file}")

def data_quality_checks():
    transformed_file = f"{DATA_DIR}/transformed_books.csv"
    
    if not os.path.exists(transformed_file):
        raise FileNotFoundError("Transformed data file is missing.")

    df = pd.read_csv(transformed_file)

    issues = []


    critical_columns = ["title", "author", "publisher", "publication_date", "ISBN", "description", "rank"]
    missing_values = df[critical_columns].isnull().sum()
    missing_issues = missing_values[missing_values > 0]
    if not missing_issues.empty:
        issues.append(f"Missing Values Found:\n{missing_issues}\n")


    duplicate_count = df.duplicated(subset=["ISBN"]).sum()
    if duplicate_count > 0:
        issues.append(f"Found {duplicate_count} duplicate ISBNs\n")


    if (df["rank"] < 1).any():
        issues.append("Some books have an invalid rank (should be ≥ 1)\n")

    if (df["weeks_on_list"] < 0).any():
        issues.append("Some books have negative `weeks_on_list`\n")


    stats = {
        "Total Books Processed": len(df),
        "Distinct Titles": df["title"].nunique(),
        "Distinct Authors": df["author"].nunique(),
        "Average Page Count": df["page_count"].dropna().mean(),
        "Average Rank": df["rank"].dropna().mean(),
    }

    #Storing Report
    with open(QUALITY_REPORT_FILE, "w") as f:
        f.write("Data Quality Report\n")
        f.write("====================\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
        f.write("\n")
        if issues:
            f.write("Issues Found:\n")
            f.write("\n".join(issues))
        else:
            f.write("No major data quality issues detected.")

    print(f"Data Quality Report generated at {QUALITY_REPORT_FILE}")


def load_to_postgres():
    transformed_file = f"{DATA_DIR}/transformed_books.csv"
    if not os.path.exists(transformed_file):
        raise FileNotFoundError("Transformed data file is missing")

    df = pd.read_csv(transformed_file)

    df.columns = df.columns.str.lower()

 
    df["isbn"] = df["isbn"].astype(str)


    with engine.begin() as conn:
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                publisher TEXT,
                publication_date TEXT,
                description TEXT,
                rank INTEGER,
                list_name TEXT,
                weeks_on_list INTEGER,
                page_count INTEGER,
                language TEXT,
                cover_image_url TEXT,
                buy_links TEXT,
                data_source TEXT,
                ingested_at TIMESTAMP
            );
        """))

        
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);"))

        
        insert_query = text("""
            INSERT INTO books (isbn, title, author, publisher, publication_date, description, rank, list_name, 
                               weeks_on_list, page_count, language, cover_image_url, buy_links, data_source, ingested_at)
            VALUES (:isbn, :title, :author, :publisher, :publication_date, :description, :rank, :list_name, 
                    :weeks_on_list, :page_count, :language, :cover_image_url, :buy_links, :data_source, :ingested_at)
            ON CONFLICT (isbn) DO UPDATE SET 
                rank = EXCLUDED.rank,
                weeks_on_list = EXCLUDED.weeks_on_list,
                ingested_at = EXCLUDED.ingested_at;
        """)

        conn.execute(insert_query, df.to_dict(orient="records"))

    print("Data loaded into PostgreSQL successfully!")

def validate_data():
    validation_report = f"{DATA_DIR}/data_validation_report.txt"

    with engine.begin() as conn:
        print("\nRunning Enhanced Data Quality Checks...\n")
        report = []

        #Completeness Check: Count total records
        total_count = conn.execute(text("SELECT COUNT(*) FROM books;")).scalar()
        report.append(f"Total Records: {total_count}")

        #Check for missing values in critical fields
        missing_critical = conn.execute(text("""
            SELECT COUNT(*) FROM books 
            WHERE isbn IS NULL OR title IS NULL OR author IS NULL OR publisher IS NULL;
        """)).scalar()
        report.append(f"Missing Critical Fields: {missing_critical}")

        #Unique Authors Count
        unique_authors = conn.execute(text("SELECT COUNT(DISTINCT author) FROM books;")).scalar()
        report.append(f"Unique Authors: {unique_authors}")

        #Check for duplicate ISBNs
        duplicates = conn.execute(text("""
            SELECT isbn, COUNT(*) FROM books 
            GROUP BY isbn HAVING COUNT(*) > 1;
        """)).fetchall()
        if duplicates:
            report.append(f"Duplicate ISBNs Found: {len(duplicates)}")
        else:
            report.append("No duplicate ISBNs found.")

        #Check for Invalid ISBNs (should be 10 or 13 digits)
        invalid_isbn = conn.execute(text("""
            SELECT COUNT(*) FROM books 
            WHERE LENGTH(isbn) NOT IN (10, 13) OR isbn !~ '^[0-9]+$';
        """)).scalar()
        report.append(f"Invalid ISBNs: {invalid_isbn}")


        #Check if buy links contain valid URLs
        invalid_links = conn.execute(text("""
            SELECT COUNT(*) FROM books 
            WHERE buy_links IS NOT NULL AND buy_links !~ '^(http|https)://';
        """)).scalar()
        report.append(f"Books with Invalid Buy Links: {invalid_links}")

        #Write report to file
        with open(validation_report, "w") as f:
            f.write("\n".join(report))

        print("\nData Validation Completed! Check:", validation_report)

dag = DAG("book_data_pipeline",
          default_args={"owner": "airflow", "start_date": datetime(2024, 1, 1)},
          schedule_interval="0 9 * * *",
          catchup=False)


extract_nyt_task = PythonOperator(task_id="extract_nytimes_books", python_callable=fetch_nytimes_books, dag=dag)
extract_openlib_task = PythonOperator(task_id="extract_openlibrary_data", python_callable=fetch_openlibrary_data, dag=dag)
extract_google_task = PythonOperator(task_id="extract_google_books_data", python_callable=fetch_google_books_data, dag=dag)
transform_task = PythonOperator(task_id="transform_data", python_callable=transform_and_enrich_data, dag=dag)
data_quality_checks_task = PythonOperator(task_id="data_quality_checks", python_callable=data_quality_checks, dag=dag)

load_task = PythonOperator(task_id="load_to_postgres", python_callable=load_to_postgres, dag=dag)
generate_data_quality_report  = PythonOperator(task_id="validate_data", python_callable=validate_data, dag=dag)

# DAG Flow: Extract → Transform → Load → Validate
extract_nyt_task >> [extract_openlib_task, extract_google_task] >> transform_task >> data_quality_checks_task >> load_task >> generate_data_quality_report
