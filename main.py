from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


DATABASE_URL = 'sqlite:///warehouse.db'  
engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



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

from datetime import datetime, timedelta

def get_salary():
    options = ("1. Kunlik (Ma'lum bir sanadagi maosh)\n"
               "2. Kunlik (Bugungi maosh)\n"
               "3. Haftalik\n"
               "4. Oylik")
    print(options)
    
    def get_custom_salary(date=None, week=False, month=False):
        cash_per_product = 3000
        try:
            # Use current date if no date is provided
            if date is None:
                date_input = input("Iltimos sanani kiriting (Masalan: 2024-12-12)\n>>>")
                date = datetime.strptime(date_input, '%Y-%m-%d').date()
            
            with SessionLocal() as session:
                # Determine the date range for weekly or monthly calculations
                if week:
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=7)
                elif month:
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=30)  # Changed from 31 to 30 for simplicity
                else:
                    start_date = date
                    end_date = date

                # Query the total number of products sold in the date range
                sold_records = session.query(SoldProductsCount).filter(SoldProductsCount.date.between(start_date, end_date)).all()
                total_products_count = sum(record.products_count for record in sold_records)
                total_earnings = total_products_count * cash_per_product

                # Query workers who attended in the date range
                workers = session.query(Worker).join(Attendance).filter(Attendance.date.between(start_date, end_date)).distinct().all()

                if not workers:
                    print("Bu sanada ishchilar mavjud emas.")
                    return

                salary_per_worker = total_earnings / len(workers)
                
                for worker in workers:
                    worker.maosh = salary_per_worker
                    print(f"Ishchi {worker.ism.title()} {worker.familiya.title()}ning maoshi: {worker.maosh:.2f}")
                
                session.commit()

        except ValueError:
            print("Sanani to'g'ri formatda kiriting (YYYY-MM-DD).")
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
    
    def get_current_daily_salary():
        get_custom_salary()

    def get_weekly_salary():
        get_custom_salary(week=True)

    def get_monthly_salary():
        get_custom_salary(month=True)
    
    # Add your menu logic here to call the appropriate functions
    choice = input("Tanlovingizni kiriting:\n>>>")
    if choice == '1':
        get_custom_salary()
    elif choice == '2':
        get_current_daily_salary()
    elif choice == '3':
        get_weekly_salary()
    elif choice == '4':
        get_monthly_salary()
    else:
        print("Noto'g'ri tanlov!")




    while True:
        print(options)
        choice = input("Iltimos ro'yxatdan birini tanlang: (Yoki, dasturni to'xtatish uchun 'exit' buyrug'ini kiriting!)\n>>>")

        if choice == "1":
            get_custom_salary()
            break
        elif choice == "2":
            get_current_daily_salary()
            break
        elif choice == "3":
            get_weekly_salary()
            break
        elif choice == "4":
            get_monthly_salary()
            break
        elif choice.lower() == "exit":
            print("Siz dasturni to'xtatdinggiz! Tashrifinggiz uchun rahmat🤗")
            break
        else:
            print("Iltimos, qayta urinib ko'ring!")

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