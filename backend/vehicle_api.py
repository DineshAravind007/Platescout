from database import get_vehicle


def get_vehicle_details(registration_number):

    if not registration_number:
        return None

    registration_number = (
        registration_number
        .upper()
        .strip()
    )

    vehicle = get_vehicle(
        registration_number
    )

    if vehicle is None:
        return None

    return {
        "registration_number":
            vehicle["registration_number"],

        "vehicle_type":
            vehicle["vehicle_type"],

        "manufacturer":
            vehicle["manufacturer"],

        "model":
            vehicle["model"],

        "fuel_type":
            vehicle["fuel_type"],

        "registration_status":
            vehicle["registration_status"],

        "insurance_status":
            vehicle["insurance_status"],

        "fitness_status":
            vehicle["fitness_status"],

        "challan_count":
            vehicle["challan_count"],

        "source":
            vehicle["source"],

        "data_type":
            vehicle["data_type"],

        "last_updated":
            vehicle["last_updated"]
    }