import os

import psycopg2
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Order Management API", version="0.1.0")


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada")
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/db/health")
def db_health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok;")
                row = cur.fetchone()
                return {"db": "ok", "result": row}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/orders")
def list_orders():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        customer VARCHAR(255) NOT NULL,
                        item VARCHAR(255) NOT NULL,
                        quantity INTEGER NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
                conn.commit()
                cur.execute("SELECT id, customer, item, quantity, created_at FROM orders ORDER BY id DESC;")
                rows = cur.fetchall()
                return rows
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/orders")
def create_order(customer: str, item: str, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity debe ser > 0")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (customer, item, quantity) VALUES (%s, %s, %s) RETURNING id;",
                    (customer, item, quantity),
                )
                new_id = cur.fetchone()["id"]
                conn.commit()
                return {"id": new_id, "customer": customer, "item": item, "quantity": quantity}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


