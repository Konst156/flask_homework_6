# Необходимо создать базу данных для интернет-магазина.
# База данных должна состоять из трёх таблиц: товары,
# заказы и пользователи.
# — Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
# — Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
# — Таблица «Пользователи» должна # содержать информацию о зарегистрированных пользователях магазина.
# • Таблица пользователей должна содержать следующие поля:
# id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
# • Таблица заказов должна содержать следующие поля:
# id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
# • Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.
# Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
# Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.


from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
import datetime
from typing import List


app = FastAPI()

# Создание подключения к базе данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Определение моделей таблиц
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)

    orders = relationship("Order", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    order_date = Column(DateTime)
    status = Column(String)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


# Модели Pydantic для каждой таблицы
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: int


class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    price: int


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    order_date: datetime.datetime
    status: str


class OrderRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_date: datetime.datetime
    status: str


# CRUD операции для каждой таблицы
@app.get("/users", response_model=List[UserRead])
def read_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserRead)
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user.dict().items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}


@app.get("/products", response_model=List[ProductRead])
def read_products():
    db = SessionLocal()
    products = db.query(Product).all()
    return products


@app.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductRead)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, product: ProductCreate):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in product.dict().items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}


@app.get("/orders", response_model=List[OrderRead])
def read_orders():
    db = SessionLocal()
    orders = db.query(Order).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderRead)
def read_order(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders", response_model=OrderRead)
def create_order(order: OrderCreate):
    db = SessionLocal()
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.put("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: int, order: OrderCreate):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    for field, value in order.dict().items():
        setattr(db_order, field, value)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted"}
