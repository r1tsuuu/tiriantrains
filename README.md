# 🦁 Tirian Trains

**Tirian Trains** is a full-stack Django application designed for managing a fictional train network within the world of Narnia. This project demonstrates backend architecture, relational database management, and advanced task automation using Celery and Redis.

**Live Demo:** [https://tiriantrains.fly.dev/](https://tiriantrains.fly.dev/)

---

## 🛠️ Tech Stack

* **Framework:** [Django](https://www.djangoproject.com/)
* **Task Queue:** [Celery](https://docs.celeryq.dev/)
* **Message Broker:** [Redis](https://redis.io/)
* **Database:** [PostgreSQL](https://www.postgresql.org/) (Production), SQLite (Local)
* **Deployment:** [Fly.io](https://fly.io/) (Dockerized)

---

## Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/tiriantrains.git](https://github.com/yourusername/tiriantrains.git)
    cd tiriantrains
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    ```

4.  **Run Migrations and Seed Data:**
    ```bash
    python manage.py migrate
    python manage.py seed_data
    ```

5.  **Start the Services:**
    * **Django Server:** `python manage.py runserver`
    * **Redis (required):** Ensure Redis is running locally.
    * **Celery Worker:** `celery -A core worker --beat -l info`
