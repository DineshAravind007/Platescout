from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from platescout_pipeline import process_vehicle_image


# ==========================================
# Flask Application
# ==========================================

app = Flask(__name__)
CORS(app)


# Temporary folder for uploaded images
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "temp_uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER 


# ==========================================
# Home Route
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "PlateScout backend is running",
        "status": "online"
    })


# ==========================================
# Analyze Vehicle
# ==========================================

@app.route("/api/analyze", methods=["POST"])
def analyze_vehicle():

    try:

        # --------------------------------------
        # Check image
        # --------------------------------------

        if "image" not in request.files:
            return jsonify({
                "success": False,
                "error": "No image received."
            }), 400

        image = request.files["image"]

        if image.filename == "":
            return jsonify({
                "success": False,
                "error": "No image selected."
            }), 400


        # --------------------------------------
        # Save uploaded image
        # --------------------------------------

        filename = "uploaded_vehicle.jpg"

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(image_path)

        print("\n================================")
        print("Image received from frontend:")
        print(image_path)
        print("================================")


        # --------------------------------------
        # Run PlateScout Pipeline
        # --------------------------------------

        result = process_vehicle_image(image_path)

        print("\n================================")
        print("PIPELINE RAW RESULT")
        print("================================")
        print(result)


        # --------------------------------------
        # Make sure result is a dictionary
        # --------------------------------------

        if not isinstance(result, dict):

            return jsonify({
                "success": False,
                "error": "Pipeline returned an invalid result."
            }), 500


        # ======================================
        # GET REGISTRATION NUMBER
        # ======================================

        registration_number = (
            result.get("registration_number")
            or result.get("plate")
            or result.get("cleaned_plate")
            or result.get("text")
            or ""
        )


        # ======================================
        # GET OCR CONFIDENCE
        # ======================================

        # Your pipeline uses "ocr_confidence".
        # Older code may use "confidence".
        # Support both.

        ocr_confidence = result.get(
            "ocr_confidence",
            result.get("confidence", 0)
        )

        try:
            ocr_confidence = float(ocr_confidence)
        except (TypeError, ValueError):
            ocr_confidence = 0.0


        # ======================================
        # GET RAW OCR TEXT
        # ======================================

        raw_text = (
            result.get("raw_text")
            or result.get("text")
            or registration_number
        )


        # ======================================
        # GET PLATE FORMAT
        # ======================================

        plate_format = result.get(
            "plate_format",
            "UNKNOWN"
        )


        # ======================================
        # GET VEHICLE INFORMATION
        # ======================================

        vehicle_information = result.get(
            "vehicle_information"
        )

        if not isinstance(vehicle_information, dict):
            vehicle_information = {}


        # --------------------------------------
        # Fill missing vehicle information
        # --------------------------------------

        vehicle_information.setdefault(
            "registration_number",
            registration_number
        )

        vehicle_information.setdefault(
            "vehicle_type",
            "Unknown"
        )

        vehicle_information.setdefault(
            "fuel_type",
            "Unknown"
        )

        vehicle_information.setdefault(
            "registration_status",
            "Unknown"
        )

        vehicle_information.setdefault(
            "insurance_status",
            "Unknown"
        )

        vehicle_information.setdefault(
            "fitness_status",
            "Unknown"
        )

        vehicle_information.setdefault(
            "challan_count",
            0
        )


        # ======================================
        # FINAL API RESPONSE
        # ======================================

        api_result = {

            "success": True,

            "registration_number":
                registration_number,

            "raw_text":
                raw_text,

            "ocr_confidence":
                ocr_confidence,

            "plate_format":
                plate_format,

            "vehicle_information":
                vehicle_information
        }


        # ======================================
        # PRINT FINAL RESULT
        # ======================================

        print("\n================================")
        print("FINAL API RESULT")
        print("================================")

        print(api_result)

        print("================================\n")


        # ======================================
        # SEND RESPONSE TO REACT
        # ======================================

        return jsonify(api_result), 200


    # ==========================================
    # ERROR HANDLING
    # ==========================================

    except Exception as e:

        print("\n================================")
        print("ERROR")
        print("================================")

        print(str(e))

        traceback.print_exc()

        print("================================\n")

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# Run Flask Server
# ==========================================

if __name__ == "__main__":

    print("======================================")
    print("        PlateScout Backend")
    print("======================================")
    print("Backend starting...")
    print("Upload folder:", UPLOAD_FOLDER)
    print("API: http://127.0.0.1:5000")
    print("======================================")

    if __name__ == "__main__":
        app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)),
            debug=False
    )