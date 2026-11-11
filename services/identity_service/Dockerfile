FROM python:3.11-slim

WORKDIR /app

COPY services/identity_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/identity_service/app/ .

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
