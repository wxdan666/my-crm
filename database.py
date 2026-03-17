from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

# Таблица связи для нескольких мастеров на одну задачу
order_workers = Table('order_workers', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id')),
    Column('worker_id', Integer, ForeignKey('workers.id'))
)

class Worker(Base):
    __tablename__ = 'workers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)
    # Связь с заказами через промежуточную таблицу
    orders = relationship("Order", secondary=order_workers, back_populates="workers")

class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    status = Column(String, default="Новая") 
    total_cost = Column(Float, default=0.0)
    # Список мастеров для этой заявки
    workers = relationship("Worker", secondary=order_workers, back_populates="orders")

class IPFinance(Base):
    __tablename__ = 'ip_finance'
    id = Column(Integer, primary_key=True)
    object_name = Column(String)    # Наименование объекта
    income = Column(Float)         # Поступило средств (Доход)
    expense = Column(Float)        # Затрачено (Расход)
    tax_rate = Column(Float, default=0.15) # Ставка 15%
    
engine = create_engine('sqlite:///repair_system.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()