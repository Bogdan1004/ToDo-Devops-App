from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from typing import List

app = FastAPI(title="Todo App - DevOps Level Up Argocd v2")

def get_db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

class Todo(BaseModel):
    title: str
    done: bool = False

@app.get("/")
def root():
    return {"status": "ok", "app": "Todo DevOps Level Up"}

@app.get("/todos")
def list_todos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM todos ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]

@app.post("/todos")
def create_todo(todo: Todo):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (title, done) VALUES (%s, %s) RETURNING id",
                (todo.title, todo.done))
    todo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": todo_id, **todo.dict()}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"deleted": todo_id}

@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))