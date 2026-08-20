from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from platescout_pipeline import process_vehicle_image
from vehicle_api import get_vehicle_details


# ==========================================
# Flask Application
# ==========================================

app = Flask(__name__)

CORS(app)


# ==========================================
# Folder for uploaded images
# ==========================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "test_images"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==========================================
# Home Route
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "message":
            "PlateScout backend is running",

        "status":
            "online"

    })


# ==========================================
# Analyze Vehicle
# ==========================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze_vehicle():

    try:

        # ======================================
        # CHECK IMAGE
        # ======================================

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "error":
                    "No image received."

            }), 400


        image = request.files["image"]


        if image.filename == "":

            return jsonify({

                "success": False,

                "error":
                    "No image selected."

            }), 400


        # ======================================
        # SAVE UPLOADED IMAGE
        # ======================================

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


        # ======================================
        # RUN PLATESCOUT PIPELINE
        # ======================================

        result = process_vehicle_image(
            image_path
        )


        print("\n================================")
        print("PIPELINE RAW RESULT")
        print("================================")

        print(result)


        # ======================================
        # CHECK PIPELINE RESULT
        # ======================================

        if not isinstance(result, dict):

            return jsonify({

                "success": False,

                "error":
                    "Pipeline returned an invalid result."

            }), 500


        # ======================================
        # CHECK PIPELINE SUCCESS
        # ======================================

        if result.get("success") is False:

            return jsonify({

                "success": False,

                "error":
                    result.get(
                        "error",
                        "Vehicle processing failed."
                    )

            }), 400


        # ======================================
        # GET REGISTRATION NUMBER
        # ======================================

        registration_number = (

            result.get(
                "registration_number"
            )

            or

            result.get(
                "plate"
            )

            or

            result.get(
                "cleaned_plate"
            )

            or

            result.get(
                "text"
            )

            or

            ""

        )


        # ======================================
        # GET OCR CONFIDENCE
        # ======================================

        ocr_confidence = result.get(

            "ocr_confidence",

            result.get(
                "confidence",
                0
            )

        )


        try:

            ocr_confidence = float(
                ocr_confidence
            )

        except (
            TypeError,
            ValueError
        ):

            ocr_confidence = 0.0


        # ======================================
        # GET RAW OCR TEXT
        # ======================================

        raw_text = (

            result.get(
                "raw_text"
            )

            or

            result.get(
                "text"
            )

            or

            registration_number

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
        #
        # IMPORTANT:
        #
        # The vehicle information now comes
        # from our SQLite database through
        # vehicle_api.py.
        #
        # OCR gives us:
        #
        #     DL7CQ1939
        #
        # Then:
        #
        #     vehicle_api.py
        #
        # searches:
        #
        #     vehicles.db
        #
        # ======================================

        vehicle_information = (
            get_vehicle_details(
                registration_number
            )
        )


        # ======================================
        # VEHICLE NOT FOUND
        # ======================================

        if vehicle_information is None:

            vehicle_information = {

                "registration_number":
                    registration_number,

                "vehicle_type":
                    "Not Found",

                "manufacturer":
                    "Not Found",

                "model":
                    "Not Found",

                "fuel_type":
                    "Not Found",

                "registration_status":
                    "Not Found",

                "insurance_status":
                    "Not Found",

                "fitness_status":
                    "Not Found",

                "challan_count":
                    0,

                "source":
                    "No database record",

                "data_type":
                    "NOT_FOUND",

                "last_updated":
                    None

            }


        # ======================================
        # FINAL API RESPONSE
        # ======================================

        api_result = {

            "success":
                True,

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

        return jsonify(
            api_result
        ), 200


    # ==========================================
    # ERROR HANDLING
    # ==========================================

    except Exception as e:

        print("\n================================")
        print("ERROR")
        print("================================")

        print(
            str(e)
        )

        traceback.print_exc()

        print("================================\n")


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ==========================================
# RUN FLASK SERVER
# ==========================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "        PlateScout Backend"
    )

    print(
        "======================================"
    )

    print(
        "Backend starting..."
    )

    print(
        "Upload folder:",
        UPLOAD_FOLDER
    )

    print(
        "API:",
        "http://127.0.0.1:5000"
    )

    print(
        "======================================"
    )


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )