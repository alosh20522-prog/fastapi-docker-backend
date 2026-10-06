from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

# إنشاء الجداول في قاعدة البيانات تلقائياً
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD & Docker Project")

# تعريف شكل البيانات المدخلة والمخرجة (Pydantic Schema)
class ItemSchema(BaseModel):
    title: str
    description: str
    price: float

    class Config:
        from_attributes = True

# 1. إضافة عنصر جديد (Create)
@app.post("/items/", response_model=ItemSchema)
def create_item(item: ItemSchema, db: Session = Depends(get_db)):
    db_item = models.Item(title=item.title, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# 2. عرض كل العناصر (Read All)
@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

# 3. عرض عنصر محدد بواسطة الـ ID (Read One)
@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 4. تعديل عنصر (Update)
@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: ItemSchema, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.title = updated_item.title
    db_item.description = updated_item.description
    db_item.price = updated_item.price
    
    db.commit()
    db.refresh(db_item)
    return db_item

# 5. حذف عنصر (Delete)
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}