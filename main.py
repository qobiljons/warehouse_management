from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
DATABASE_URL = 'sqlite:///warehouse.db'  # SQLite database file
engine = create_engine(DATABASE_URL, echo=True)  # Echo=True to log SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Worker(Base):
    __tablename__ = 'workers'
    
    id = Column(Integer, primary_key=True, index=True)
    ism = Column(String, index=True)
    familiya = Column(String, index=True)
    maosh = Column(Float, nullable=True)

    attendances = relationship("Attendance", back_populates="worker")
    
    def __repr__(self):
        return f"<Worker(id={self.id}, name={self.first_name} {self.last_name}, salary_per_unit={self.salary_per_unit})>"


class Attendance(Base):
    __tablename__ = 'attendances'

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    date = Column(Date, index=True)

    # Define relationship to Worker
    worker = relationship("Worker", back_populates="attendances")


class SoldProductsCount(Base):
    __tablename__ = 'sold_products_counts'

    id = Column(Integer, primary_key=True, index=True)
    product_count = Column(Integer, nullable=False)
    date = Column(Date, index=True)


Base.metadata.create_all(bind=engine)


# Functions
def add_worker():
    while True:
        first_name = input("Iltimos yangi ishchining ismini kiriting\n>>>")
        last_name = input("Iltimos yangi ishchining familiyasini kiriting\n>>>")
        
        if first_name.strip() == "" or last_name.strip() == "":
            print("Ism yoki familiya bo'sh bolishi mumkin emas! Iltimos, qayta urinib ko'ring.")
            continue
        
        try:
            session = SessionLocal()
            new_worker = Worker(ism=first_name.lower(), familiya=last_name.lower(), maosh=0.0)  # Default value for salary_per_unit
            session.add(new_worker)
            session.commit()
            print(f"Ishchi {first_name} {last_name} muvaffaqiyatli qo'shildi.")
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            session.rollback()
        finally:
            session.close()
            break


def get_workers():
    try:
        with SessionLocal() as session:
            workers = session.query(Worker).all()
            
            if not workers:
                print("Hozircha ishchilar mavjud emas.")
                return
           
            print(f"{'ID':<5} {'Ism':<20} {'Familiya':<20} {'Maosh':<20}")
            print("-" * 65)  
            for worker in workers:
                print(f"{worker.id:<5} {worker.ism.title():<20} {worker.familiya.title():<20} {worker.maosh:<20.2f}")
                
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")


def insert_attendance():
    name = input("Iltimos ishchining ismini kiriting\n>>>")
    try:
        with SessionLocal() as session:
            worker = session.query(Worker).filter_by(ism=name.lower()).first()
            
            if worker:
                date = datetime.now().date()
                new_attendance = Attendance(worker_id=worker.id, date=date)
                session.add(new_attendance)
                session.commit()
                print(f"Ishchi {name} uchun yangi ishtirok qo'shildi. Sana: {date}")
            else:
                print(f"Ishchi {name} mavjud emas.")
                
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")


def add_sold_products():
    product_count = int(input("Sotilgan maxsulotlar sonini kiriting\n>>>"))
    try:
        with SessionLocal() as session:
                date = datetime.now().date()
                sold_products = SoldProductsCount(product_count=product_count, date=date)
                session.add(sold_products)
                session.commit()
                print(f"{product_count} ta yangi maxsulotlar qo'shildi. Sana: {date}")
    except ValueError:
        print("Sotilgan maxsulotlar soni raqam bo'lishi kerak!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")


def main():
    options = f"1.Kelgan ishchilarni kiritish.\n2.Chiqarilgan maxsulotlar sonini qo'shish.\n3.Yangi ishchi qo'shish\n4.Ishchilar ro'yhatini ko'ish.\n5.Maosh"

    while True:
        print(options)
        choice = input("Iltimos ro'yxatdan birini tanlang: (Yoki, dasturni to'xtatish uchun 'exit' buyrug'ini kiriting!)\n>>>")

        if choice == "1":
            insert_attendance()
        elif choice == "2":
            add_sold_products()
        elif choice == "3":
            add_worker()
        elif choice == "4":
            get_workers()
        elif choice == "5":
            pass
        elif choice.lower() == "exit":
            print("Siz dasturni to'xtatdinggiz! Tashrifinggiz uchun rahmat🤗")
            break


if __name__ == "__main__":
    main()