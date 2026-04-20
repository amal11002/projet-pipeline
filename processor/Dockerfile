FROM python:3.9-bullseye

RUN apt-get update && apt-get install -y openjdk-11-jdk procps gcc python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processor.py .

CMD ["python", "processor.py"]