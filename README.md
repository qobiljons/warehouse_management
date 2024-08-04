# Warehouse Management System

This project is a simple warehouse management system built with SQLAlchemy and SQLite. It allows you to manage workers, track attendances, record sold products, and calculate salaries based on sales and attendance data.

## Features

1. **Add New Worker**: Register new workers with their first name and last name.
2. **Insert Attendance**: Record attendance for workers based on their names.
3. **Add Sold Products**: Log the count of sold products.
4. **Calculate Salary**:
    - **Today's Salary**: Calculate the salary for workers based on today's sales and attendance.
    - **Salary by Date Range**: Calculate and export salary information for a specified date range to a JSON file.

## Requirements

- Python 3.x
- SQLAlchemy
- SQLite (bundled with Python)
- `json` (standard Python library)

## Installation

1. **Clone the Repository:**

   ```sh
   git clone <repository-url>


2. **Install dependencies:**

   ```sh
   pip install sqlalchemy
3. **Run the file:**

   ```sh
   python warehouse_management.py

