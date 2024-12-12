from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from .schemas import TodoCreate, TodoResponse
from .models import Todo
from .database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/todos', response_model = TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit() #更新資料庫
    db.refresh(db_todo)
    return db_todo

@router.get('/todos', response_model = list[TodoResponse])
def read_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

@router.get('/todo/{todo_id}', response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return HTTPException(status_code=404, details='Todo not found')
    return db_todo

@router.put('/todo/{todo_id}', response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, details='Todo not found')
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.delete('/todo/{todo_id}')
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, details='Todo not found')
    db.commit()
    db.refresh(db_todo)
    return {'detail': 'Todo deleted successfully'}