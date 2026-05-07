FROM python:3.11-slim

WORKDIR /app

# Pull in the requirements first to take advantage of Docker's layer caching.
# This makes subsequent builds much faster if you haven't changed your dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now bring in the actual application code
COPY . .

# FastAPI usually runs on 8000
EXPOSE 8000

# Fire up the uvicorn server with 2 workers for a bit of concurrency
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
