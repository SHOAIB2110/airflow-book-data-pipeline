# 📚 Book Data Pipeline

A fully automated **book data pipeline** using **Apache Airflow** (or Prefect), integrated with APIs (**NYT, OpenLibrary, Google Books**) and storing results in **PostgreSQL**.

---

## 🏗 Project Overview & Architecture Diagram

The pipeline extracts book data from external APIs, validates and transforms it, and loads it into a PostgreSQL database. The entire process is orchestrated using **Airflow DAGs** (or Prefect flows).

\
👉 *Replace **`IMG_2.jpg`** with the actual path to your image*

---

## 🔧 Installation & Setup

### 1️⃣ Install Docker Desktop

This project runs inside Docker containers. **Install Docker Desktop** before proceeding:

- [Download Docker](https://www.docker.com/products/docker-desktop)
- Follow the installation instructions for your OS.

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/book_data_pipeline.git
cd book_data_pipeline
```

### 3️⃣ Set Up Environment Variables

Before running the pipeline, export the API keys and database variables:

```bash
export API_KEY_NYT=your-nyt-api-key
export API_KEY_GOOGLE=your-google-api-key
```

✅ **Verify Environment Variables:**

```bash
echo $API_KEY_NYT
echo $API_KEY_GOOGLE
```

### 4️⃣ Install Dependencies (Optional for Local Execution)

Create a **virtual environment** and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## 🚀 Running the Pipeline with Docker

### 1️⃣ Build and Start Containers

```bash
docker-compose up --build -d
```

### 2️⃣ Check Running Containers

```bash
docker ps
```

---

## 🌐 Access Airflow UI

### 🔑 Default Credentials

- **URL:** [http://localhost:8080](http://localhost:8080)
- **Username:** `airflow`
- **Password:** `airflow`

👉 *Once inside Airflow, navigate to **`book_pipeline`** and trigger the DAG manually.*

---

## 📊 Database Inspection

To ensure data completeness and quality, run the following queries in **PostgreSQL**:

```sql
SELECT * FROM books LIMIT 10;
SELECT COUNT(*) FROM books WHERE title IS NULL;
```

---

## 🛠 Debugging & Logs

### 1️⃣ Check Airflow Logs

```bash
docker logs -f airflow_scheduler
```

### 2️⃣ Check Task Logs

```bash
airflow tasks logs book_pipeline extract_books
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create a feature branch**
3. **Commit changes**
4. **Push and create a Pull Request**

---

## 📜 License

This project is licensed under the MIT License.

---

Happy Coding! 🚀

