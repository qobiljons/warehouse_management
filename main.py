from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Double
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
from sqlalchemy import func
import json


DATABASE_URL = 'sqlite:///warehouse.db'  
engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
PAYMENT = 300


class Worker(Base):
    __tablename__ = 'workers'
    
    id = Column(Integer, primary_key=True, index=True)
    ism = Column(String, index=True)
    familiya = Column(String, index=True)

    attendances = relationship("Attendance", back_populates="worker")
    
    def __repr__(self):
        return f"<Worker(id={self.id}, name={self.first_name} {self.last_name}, salary_per_unit={self.salary_per_unit})>"


class Attendance(Base):
    __tablename__ = 'attendances'

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    date = Column(Date, index=True)
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

def get_salary():
    options = "1.Bugungi\n2.Sana Orqali"
    
    def calculate_salary(date: datetime.date = datetime.now().date()):
        with SessionLocal() as session:
            total_sold = session.query(func.sum(SoldProductsCount.product_count)).filter(SoldProductsCount.date == date).scalar() or 0
            attendance_records = session.query(Attendance).filter_by(date=date).all()
            workers_today = len(attendance_records)
            
            if workers_today > 0:
                earned_money = (total_sold / workers_today) * PAYMENT
                print(f"{date} sana uchun jami sotilgan maxsulotlar soni: {total_sold}")
                print(f"{date} sana uchun ishchilar soni: {workers_today}")
                print(f"Har bir ishchi uchun to'lanadigan maosh: {earned_money:.2f} so'm")
            else:
                print(f"{date} sana uchun hech qanday ishtirokchi mavjud emas.")
    
    def calculate_salary_for_range():
        def get_dates_in_range(start_date_str: str, end_date_str: str) -> list:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                
                if start_date > end_date:
                    raise ValueError("End date must be after or the same as start date.")
                
                date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
                return date_list

            except ValueError as e:
                print(f"Error: {e}")
                return []

        start_date = input("Boshlanish kuni (YYYY-MM-DD): ")
        end_date = input("Tugash sanasi (YYYY-MM-DD): ")
        
        dates = get_dates_in_range(start_date, end_date)
        daily_info = {}
        income = {}
        
        with SessionLocal() as session:
            for date in dates:
                day = date.strftime("%Y-%m-%d")
                total_sold = session.query(func.sum(SoldProductsCount.product_count)).filter(SoldProductsCount.date == day).scalar() or 0
                attendance_records = session.query(Attendance).filter_by(date=day).all()
                workers_attended = len(attendance_records)
                
                if workers_attended > 0:
                    earned_money = (total_sold / workers_attended) * PAYMENT
                    daily_info[day] = {
                        "earned_money": earned_money,
                        "workers": [session.query(Worker).filter_by(id=record.worker_id).first().ism for record in attendance_records],
                        "total_sold": total_sold,
                    }
                    for worker in daily_info[day]["workers"]:
                        if worker in income:
                            income[worker] += earned_money
                        else:
                            income[worker] = earned_money
        
        try:
            data = {
                "daily_info": daily_info,
                "income": income
            }
            with open('data.json', 'w') as file:
                json.dump(data, file, indent=4)
            print("Data has been written to data.json")
        except IOError as e:
            print(f"Error writing to file: {e}")
        except TypeError as e:
            print(f"Error serializing data: {e}")

    while True:
        print(options)
        choice = input("Iltimos ro'yxatdan birini tanlang: (Yoki, dasturni to'xtatish uchun 'exit' buyrug'ini kiriting!)\n>>>")

        if choice == "1":
            calculate_salary(date=datetime.now().date())
            break
        elif choice == "2":
            calculate_salary_for_range()
            break
        elif choice.lower() == "exit":
            print("Siz dasturni to'xtatdinggiz! Tashrifinggiz uchun rahmat🤗")
            break
        else:
            print("Iltimos, qayta urinib ko'ring.")


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
            get_salary()
        elif choice.lower() == "exit":
            print("Siz dasturni to'xtatdinggiz! Tashrifinggiz uchun rahmat🤗")
            break


if __name__ == "__main__":
    main()