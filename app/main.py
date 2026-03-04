from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="Todo App - DevOps Level Up Endava")

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

@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todo App - DevOps Level Up Endava</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 40px;
      width: 100%;
      max-width: 600px;
      box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }
    h1 {
      color: #e94560;
      font-size: 2rem;
      margin-bottom: 8px;
      text-align: center;
    }
    .subtitle {
      color: rgba(255,255,255,0.4);
      text-align: center;
      font-size: 0.85rem;
      margin-bottom: 30px;
    }
    .input-row {
      display: flex;
      gap: 10px;
      margin-bottom: 25px;
    }
    input[type="text"] {
      flex: 1;
      padding: 12px 18px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.15);
      background: rgba(255,255,255,0.08);
      color: white;
      font-size: 1rem;
      outline: none;
      transition: border-color 0.2s;
    }
    input[type="text"]:focus { border-color: #e94560; }
    input[type="text"]::placeholder { color: rgba(255,255,255,0.3); }
    button.add-btn {
      padding: 12px 22px;
      background: #e94560;
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    button.add-btn:hover { background: #c73652; }
    #todo-list { list-style: none; }
    #todo-list li {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.05);
      border-radius: 10px;
      margin-bottom: 10px;
      border: 1px solid rgba(255,255,255,0.07);
      transition: background 0.2s;
    }
    #todo-list li:hover { background: rgba(255,255,255,0.09); }
    #todo-list li.done span { text-decoration: line-through; color: rgba(255,255,255,0.3); }
    #todo-list li span { flex: 1; color: rgba(255,255,255,0.85); font-size: 0.95rem; }
    .check-btn {
      background: none;
      border: 2px solid rgba(255,255,255,0.2);
      border-radius: 50%;
      width: 26px; height: 26px;
      cursor: pointer;
      color: #4ecca3;
      font-size: 14px;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.2s;
    }
    .check-btn:hover { border-color: #4ecca3; background: rgba(78,204,163,0.1); }
    .del-btn {
      background: none;
      border: none;
      color: rgba(255,255,255,0.2);
      font-size: 18px;
      cursor: pointer;
      transition: color 0.2s;
    }
    .del-btn:hover { color: #e94560; }
    .empty {
      text-align: center;
      color: rgba(255,255,255,0.25);
      padding: 30px;
      font-style: italic;
    }
    .badge {
      display: inline-block;
      background: rgba(78,204,163,0.15);
      color: #4ecca3;
      border-radius: 20px;
      padding: 3px 12px;
      font-size: 0.75rem;
      margin: 0 auto 20px;
      display: block;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📋 Todo App</h1>
    <span class="badge">🚀 DevOps Level Up GitOps</span>
    <div class="input-row">
      <input type="text" id="new-todo" placeholder="Adauga un task nou..." onkeydown="if(event.key==='Enter') addTodo()">
      <button class="add-btn" onclick="addTodo()">＋ Add</button>
    </div>
    <ul id="todo-list"><li class="empty">Se incarca...</li></ul>
  </div>
  <script>
    async function loadTodos() {
      const res = await fetch('/todos');
      const todos = await res.json();
      const ul = document.getElementById('todo-list');
      if (!todos.length) { ul.innerHTML = '<li class="empty">Niciun task inca. Adauga unul! 🎯</li>'; return; }
      ul.innerHTML = todos.map(t => `
        <li class="${t.done ? 'done' : ''}" id="todo-${t.id}">
          <button class="check-btn" onclick="toggleTodo(${t.id})">✓</button>
          <span>${t.title}</span>
          <button class="del-btn" onclick="deleteTodo(${t.id})">✕</button>
        </li>`).join('');
    }
    async function addTodo() {
      const inp = document.getElementById('new-todo');
      if (!inp.value.trim()) return;
      await fetch('/todos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({title: inp.value}) });
      inp.value = '';
      loadTodos();
    }
    async function deleteTodo(id) {
      await fetch('/todos/' + id, { method: 'DELETE' });
      loadTodos();
    }
    async function toggleTodo(id) {
      const li = document.getElementById('todo-' + id);
      li.classList.toggle('done');
    }
    loadTodos();
  </script>
</body>
</html>
"""

@app.get("/todos")
def list_todos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM todos ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]

@app.post("/todos")
def create_todo(todo: Todo):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (title, done) VALUES (%s, %s) RETURNING id", (todo.title, todo.done))
    todo_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return {"id": todo_id, **todo.dict()}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit(); cur.close(); conn.close()
    return {"deleted": todo_id}

@app.get("/health")
def health():
    try:
        conn = get_db(); conn.close()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
