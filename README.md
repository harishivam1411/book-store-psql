# Running the Microservices

## Start the Bookstore Microservice (Producer, FastAPI)

```bash
uvicorn store.main:app --host 127.0.0.1 --port 8000 --reload
```

## Start the Log Microservice (FastAPI)

```bash
uvicorn store.log:app --host 127.0.0.1 --port 9000 --reload
```

## Start the Transaction Microservice (Consumer)

```bash
python store/transaction.py
```

## Start the Analytics Microservice (Consumer)

```bash
python store/analytics.py
```
