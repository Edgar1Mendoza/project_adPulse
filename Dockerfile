FROM apache/airflow:3.3.2-python3.12

WORKDIR /opt/airflow/project

COPY requirements.txt pyproject.toml ./
COPY src/ ./src

RUN pip install --no-cache-dir -r requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt"