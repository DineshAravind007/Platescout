import sqlite3
from pathlib import Path


# ============================================
# DATABASE PATH
# ============================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "vehicles.db"


# ============================================
# CONNECT TO DATABASE
# ============================================

def get_connection():

    connection = sqlite3.connect(
        str(DATABASE)
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================
# CREATE TABLE
# ============================================

def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            registration_number TEXT UNIQUE NOT NULL,

            vehicle_type TEXT,

            manufacturer TEXT,

            model TEXT,

            fuel_type TEXT,

            registration_status TEXT,

            insurance_status TEXT,

            fitness_status TEXT,

            challan_count INTEGER,

            source TEXT,

            data_type TEXT,

            last_updated TEXT
        )
    """)

    connection.commit()

    connection.close()


# ============================================
# INSERT DEMO VEHICLE
# ============================================

def insert_vehicle(
    registration_number,
    vehicle_type,
    manufacturer,
    model,
    fuel_type,
    registration_status,
    insurance_status,
    fitness_status,
    challan_count
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO vehicles (

            registration_number,
            vehicle_type,
            manufacturer,
            model,
            fuel_type,
            registration_status,
            insurance_status,
            fitness_status,
            challan_count,
            source,
            data_type,
            last_updated

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        registration_number,
        vehicle_type,
        manufacturer,
        model,
        fuel_type,
        registration_status,
        insurance_status,
        fitness_status,
        challan_count,

        "PlateScout Demo Database",

        "DEMO",

        "2026-08-19"
    ))

    connection.commit()

    connection.close()


# ============================================
# INSERT DEMO RECORDS
# ============================================

def insert_demo_data():

    # 1
    insert_vehicle(
        "DL7CQ1939",
        "SUV",
        "Hyundai",
        "Creta",
        "Diesel",
        "Active",
        "Valid",
        "Valid",
        2
    )

    # 2
    insert_vehicle(
        "TN87C5106",
        "Hatchback",
        "Maruti Suzuki",
        "Swift",
        "Petrol",
        "Active",
        "Valid",
        "Valid",
        0
    )

    # 3
    insert_vehicle(
        "KL56Q9009",
        "Sedan",
        "Honda",
        "City",
        "Petrol",
        "Active",
        "Valid",
        "Valid",
        1
    )

    # 4
    insert_vehicle(
        "KA01AB1234",
        "SUV",
        "Tata",
        "Nexon",
        "Petrol",
        "Active",
        "Valid",
        "Valid",
        0
    )

    # 5
    insert_vehicle(
        "MH12DE3456",
        "Sedan",
        "Toyota",
        "Etios",
        "Diesel",
        "Active",
        "Expired",
        "Valid",
        3
    )

    # 6
    insert_vehicle(
        "TN38AB1234",
        "Hatchback",
        "Hyundai",
        "i20",
        "Petrol",
        "Active",
        "Valid",
        "Valid",
        0
    )

    # 7
    insert_vehicle(
        "AP09XY5678",
        "SUV",
        "Kia",
        "Seltos",
        "Diesel",
        "Active",
        "Valid",
        "Valid",
        1
    )

    # 8
    insert_vehicle(
        "KL07MN2468",
        "Sedan",
        "Maruti Suzuki",
        "Ciaz",
        "Petrol",
        "Active",
        "Valid",
        "Valid",
        0
    )


# ============================================
# GET VEHICLE
# ============================================

def get_vehicle(registration_number):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM vehicles

        WHERE registration_number = ?
    """, (
        registration_number.upper(),
    ))

    vehicle = cursor.fetchone()

    connection.close()

    if vehicle:

        return dict(vehicle)

    return None


# ============================================
# INITIALIZE DATABASE
# ============================================

def initialize_database():

    print("Creating database...")

    create_table()

    print("Adding demo vehicle records...")

    insert_demo_data()

    print("Database ready!")

    print(
        "Database location:",
        DATABASE
    )


# ============================================
# TEST DATABASE
# ============================================

if __name__ == "__main__":

    initialize_database()

    print("\nTesting database...")

    vehicle = get_vehicle(
        "DL7CQ1939"
    )

    if vehicle:

        print("\nVehicle found:")

        print(vehicle)

    else:

        print("\nVehicle not found.")