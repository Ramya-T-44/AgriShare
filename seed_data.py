"""
==========================================
AgriShare - Database Seeder
==========================================
Run this AFTER schema.sql has created the database & tables:
    python seed_data.py

It inserts demo users, equipment listings, and bookings.
All demo accounts use the password:  password123
==========================================
"""
import pyodbc
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=AgriShareDB;"
    "Trusted_Connection=yes;"
)


def main():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()

    # ---- Clear existing data (safe to re-run) ----
    cursor.execute("DELETE FROM Bookings")
    cursor.execute("DELETE FROM Equipment")
    cursor.execute("DELETE FROM Users")

    # ---- Demo Users ----
    users = [
        ("Ramesh Kumar",  "ramesh@gmail.com",  "9876543210", "Rampur"),
        ("Sita Devi",     "sita@gmail.com",     "9876543211", "Rampur"),
        ("Gopal Singh",   "gopal@gmail.com",    "9876543212", "Kisan Nagar"),
        ("Lakshmi Bai",   "lakshmi@gmail.com",  "9876543213", "Kisan Nagar"),
        ("Hari Prasad",   "hari@gmail.com",     "9876543214", "Green Valley"),
    ]

    for full_name, email, phone, village in users:
        cursor.execute(
            "INSERT INTO Users (FullName, Email, PasswordHash, PhoneNumber, VillageName) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, generate_password_hash("password123"), phone, village)
        )

    # ---- Demo Equipment (title, category, hourly, daily, owner_index 1-based) ----
    equipment = [
        ("Mahindra Tractor 475",    "Tractor",          500, 3500, 1),
        ("John Deere Harvester",    "Harvester",       1200, 8000, 2),
        ("Kirloskar Irrigation Pump", "Irrigation Pump", 200, 1200, 3),
        ("Swaraj Tractor 744",      "Tractor",          550, 3800, 4),
        ("Mini Harvester Combo",    "Harvester",       1000, 6500, 5),
        ("Water Pump 5HP",          "Irrigation Pump",  180, 1000, 1),
        ("Tractor Trolley",         "Tractor",          300, 1800, 2),
    ]

    for title, category, hr, dr, owner_idx in equipment:
        cursor.execute(
            "INSERT INTO Equipment (Title, Category, HourlyRate, DailyRate, OwnerID, IsAvailable) VALUES (?, ?, ?, ?, ?, 1)",
            (title, category, hr, dr, owner_idx)
        )

    # ---- Demo Bookings (equipment_idx, renter_idx, start_days_from_now, end_days_from_now, cost, status) ----
    now = datetime.now()
    bookings = [
        (1, 2, 1, 2, 4000, "Pending"),
        (2, 3, 2, 3, 8000, "Approved"),
        (3, 4, 3, 4, 1200, "Pending"),
        (4, 5, 2, 3, 5500, "Approved"),
        (5, 1, 4, 5, 6500, "Pending"),
    ]

    for eq_idx, renter_idx, s_days, e_days, cost, status in bookings:
        start = now + timedelta(days=s_days)
        end = now + timedelta(days=e_days)
        cursor.execute(
            "INSERT INTO Bookings (EquipmentID, RenterID, StartDate, EndDate, TotalCost, BookingStatus) VALUES (?, ?, ?, ?, ?, ?)",
            (eq_idx, renter_idx, start, end, cost, status)
        )

    conn.commit()
    conn.close()

    print("=" * 55)
    print("✅  AgriShare demo data inserted successfully!")
    print("=" * 55)
    print("\n👤  Demo Accounts  (password for all:  password123)\n")
    for name, email, *_ in users:
        print(f"    {name:<16} →  {email}")
    print("\n🚜  Run `python app.py` and log in to explore.")


if __name__ == "__main__":
    main()

