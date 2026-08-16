def get_vehicle_data(plate_number):

    vehicle = {
        "registration_number": plate_number,
        "vehicle_type": "Car",
        "fuel_type": "Petrol",
        "registration_status": "Active",
        "insurance_status": "Active",
        "fitness_status": "Valid",
        "challan_count": 0
    }

    return vehicle


if __name__ == "__main__":

    plate = "KL56Q9009"

    data = get_vehicle_data(plate)

    print("\nVehicle Information")
    print("-------------------")

    for key, value in data.items():
        print(f"{key}: {value}")