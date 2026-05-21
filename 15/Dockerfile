FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY . .

# expose port
EXPOSE 8000

# run app
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]