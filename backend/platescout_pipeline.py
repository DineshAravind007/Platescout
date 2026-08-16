from ultralytics import YOLO
import cv2
import easyocr
import re
import os
from pathlib import Path


# ==================================================
# PROJECT PATHS
# ==================================================

# Project root:
# E:\PlateScout
BASE_DIR = Path(__file__).resolve().parent.parent

# Models are stored in:
# E:\PlateScout\models
MODELS_DIR = BASE_DIR / "models"

# Model file
BEST_MODEL = MODELS_DIR / "best.pt"

# Output folder:
# E:\PlateScout\outputs
OUTPUT_DIR = BASE_DIR / "outputs"


print("===================================")
print("PlateScout Pipeline Started")
print("===================================")

print("Project directory:", BASE_DIR)
print("Models directory:", MODELS_DIR)
print("YOLO model:", BEST_MODEL)
print("Output directory:", OUTPUT_DIR)


# ==================================================
# CHECK MODEL
# ==================================================

if not BEST_MODEL.exists():
    raise FileNotFoundError(
        f"YOLO model not found:\n{BEST_MODEL}"
    )


# ==================================================
# OCR READER
# ==================================================

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


# ==================================================
# YOLO MODEL
# ==================================================

model = YOLO(str(BEST_MODEL))


# ==================================================
# OCR CLEANING
# ==================================================

def clean_plate_text(text):
    """
    Clean OCR output.

    Keep only English letters and numbers.
    """

    text = text.upper()

    # Remove spaces and special characters
    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# ==================================================
# PLATE FORMAT VALIDATION
# ==================================================

def is_valid_plate(text):
    """
    General Indian vehicle registration format.

    Examples:
        TN87C5106
        KL56Q9009
        KA01AB1234
    """

    pattern = (
        r"^[A-Z]{2}"
        r"[0-9]{1,2}"
        r"[A-Z]{1,3}"
        r"[0-9]{1,4}$"
    )

    return re.match(
        pattern,
        text
    ) is not None


# ==================================================
# OCR
# ==================================================

def perform_ocr(plate):

    print("\nRunning enhanced OCR...")

    # ----------------------------------------------
    # Make sure plate is valid
    # ----------------------------------------------

    if plate is None or plate.size == 0:
        return None, 0.0


    # ----------------------------------------------
    # Resize
    # ----------------------------------------------

    upscaled = cv2.resize(
        plate,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )


    # ----------------------------------------------
    # Grayscale
    # ----------------------------------------------

    gray = cv2.cvtColor(
        upscaled,
        cv2.COLOR_BGR2GRAY
    )


    # ----------------------------------------------
    # CLAHE enhancement
    # ----------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)


    # ----------------------------------------------
    # Sharpen image
    # ----------------------------------------------

    sharpen_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (3, 3)
    )

    sharpened = cv2.morphologyEx(
        enhanced,
        cv2.MORPH_GRADIENT,
        sharpen_kernel
    )


    # ----------------------------------------------
    # OTSU threshold
    # ----------------------------------------------

    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )


    # ----------------------------------------------
    # Adaptive threshold
    # ----------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


    # ----------------------------------------------
    # Create output directory
    # ----------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # ----------------------------------------------
    # Save preprocessing results
    # ----------------------------------------------

    cv2.imwrite(
        str(OUTPUT_DIR / "ocr_original.jpg"),
        upscaled
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "ocr_enhanced.jpg"),
        enhanced
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "ocr_otsu.jpg"),
        otsu
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "ocr_adaptive.jpg"),
        adaptive
    )


    # ----------------------------------------------
    # OCR configurations
    # ----------------------------------------------

    images = [
        ("original", upscaled),
        ("enhanced", enhanced),
        ("otsu", otsu),
        ("adaptive", adaptive)
    ]

    all_results = []


    # ----------------------------------------------
    # Run OCR
    # ----------------------------------------------

    for name, img in images:

        print(
            f"\nOCR method: {name}"
        )

        try:

            results = reader.readtext(
                img,
                detail=1,
                paragraph=False,
                allowlist=(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "0123456789"
                )
            )


            for result in results:

                if len(result) >= 3:

                    text = result[1]

                    confidence = float(
                        result[2]
                    )

                    cleaned = clean_plate_text(
                        text
                    )


                    if cleaned:

                        print(
                            f"Detected: {text} | "
                            f"Cleaned: {cleaned} | "
                            f"Confidence: "
                            f"{confidence:.2f}"
                        )


                        all_results.append(
                            {
                                "text": cleaned,
                                "confidence": confidence,
                                "method": name
                            }
                        )


        except Exception as error:

            print(
                f"OCR error in {name}: "
                f"{error}"
            )


    # ----------------------------------------------
    # No OCR result
    # ----------------------------------------------

    if not all_results:

        return None, 0.0


    # ----------------------------------------------
    # Remove duplicate results
    # ----------------------------------------------

    unique_results = {}


    for result in all_results:

        text = result["text"]

        if (
            text not in unique_results
            or
            result["confidence"]
            >
            unique_results[text]["confidence"]
        ):

            unique_results[text] = result


    results = list(
        unique_results.values()
    )


    # ----------------------------------------------
    # Prefer VALID Indian plate formats
    # ----------------------------------------------

    valid_results = [
        result
        for result in results
        if is_valid_plate(
            result["text"]
        )
    ]


    if valid_results:

        # Highest confidence valid result

        best = max(
            valid_results,
            key=lambda x: x["confidence"]
        )

    else:

        # Otherwise use highest confidence result

        best = max(
            results,
            key=lambda x: x["confidence"]
        )


    # ----------------------------------------------
    # Print best OCR result
    # ----------------------------------------------

    print(
        "\n==================================="
    )

    print(
        "BEST OCR RESULT"
    )

    print(
        "==================================="
    )

    print(
        "Plate:",
        best["text"]
    )

    print(
        "Confidence:",
        best["confidence"]
    )

    print(
        "Method:",
        best["method"]
    )


    return (
        best["text"],
        best["confidence"]
    )


# ==================================================
# MAIN PIPELINE
# ==================================================

def run_pipeline(image_path):

    print(
        "\n==================================="
    )

    print(
        "Processing:",
        image_path
    )

    print(
        "==================================="
    )


    # ----------------------------------------------
    # Convert path to absolute path
    # ----------------------------------------------

    image_path = Path(image_path)

    if not image_path.is_absolute():

        image_path = (
            BASE_DIR / image_path
        )


    # ----------------------------------------------
    # Read image
    # ----------------------------------------------

    image = cv2.imread(
        str(image_path)
    )


    if image is None:

        print(
            "ERROR: Could not read image."
        )

        return {
            "success": False,
            "error": "Could not read image"
        }


    # ----------------------------------------------
    # YOLO detection
    # ----------------------------------------------

    results = model(image)

    result = results[0]


    # ----------------------------------------------
    # Check detection
    # ----------------------------------------------

    if len(result.boxes) == 0:

        print(
            "No license plate detected."
        )

        return {
            "success": False,
            "error":
                "No license plate detected"
        }


    print(
        "License plate detected!"
    )


    # ----------------------------------------------
    # Get best detection
    # ----------------------------------------------

    best_box = None

    best_confidence = 0


    for box, confidence in zip(
        result.boxes.xyxy,
        result.boxes.conf
    ):

        conf = float(
            confidence.cpu().numpy()
        )


        if conf > best_confidence:

            best_confidence = conf

            best_box = (
                box.cpu().numpy()
            )


    # ----------------------------------------------
    # Safety check
    # ----------------------------------------------

    if best_box is None:

        return {
            "success": False,
            "error":
                "Could not determine "
                "license plate location"
        }


    # ----------------------------------------------
    # Coordinates
    # ----------------------------------------------

    x1, y1, x2, y2 = map(
        int,
        best_box
    )


    print(
        "Plate coordinates:"
    )

    print(
        x1,
        y1,
        x2,
        y2
    )


    # ----------------------------------------------
    # Add small padding
    # ----------------------------------------------

    height, width = image.shape[:2]

    padding = 5


    x1 = max(
        0,
        x1 - padding
    )

    y1 = max(
        0,
        y1 - padding
    )

    x2 = min(
        width,
        x2 + padding
    )

    y2 = min(
        height,
        y2 + padding
    )


    # ----------------------------------------------
    # Crop plate
    # ----------------------------------------------

    plate = image[
        y1:y2,
        x1:x2
    ]


    if plate.size == 0:

        return {
            "success": False,
            "error":
                "Plate crop failed"
        }


    # ----------------------------------------------
    # Save crop
    # ----------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    crop_path = (
        OUTPUT_DIR /
        "pipeline_plate_crop.jpg"
    )


    cv2.imwrite(
        str(crop_path),
        plate
    )


    print(
        "Plate cropped successfully!"
    )

    print(
        "Saved to:",
        crop_path
    )


    # ----------------------------------------------
    # OCR
    # ----------------------------------------------

    plate_text, ocr_confidence = (
        perform_ocr(plate)
    )


    # ----------------------------------------------
    # OCR failed
    # ----------------------------------------------

    if not plate_text:

        print(
            "No text detected."
        )

        return {
            "success": False,
            "error":
                "No text detected"
        }


    # ----------------------------------------------
    # Validate plate
    # ----------------------------------------------

    if is_valid_plate(
        plate_text
    ):

        plate_format = "VALID"

    else:

        plate_format = "INVALID"


    # ----------------------------------------------
    # Print final result
    # ----------------------------------------------

    print(
        "\n==================================="
    )

    print(
        "FINAL PIPELINE RESULT"
    )

    print(
        "==================================="
    )

    print(
        "Detected text:",
        plate_text
    )

    print(
        "OCR Confidence:",
        ocr_confidence
    )

    print(
        "Plate format:",
        plate_format
    )


    # ----------------------------------------------
    # Return result
    # ----------------------------------------------

    return {

        "success": True,

        "registration_number":
            plate_text,

        "raw_text":
            plate_text,

        "ocr_confidence":
            ocr_confidence,

        "plate_format":
            plate_format
    }


# ==================================================
# PROCESS VEHICLE IMAGE
# ==================================================

def process_vehicle_image(image_path):

    return run_pipeline(
        image_path
    )


# ==================================================
# DIRECT TEST
# ==================================================

if __name__ == "__main__":

    test_image = (
        BASE_DIR /
        "test_images" /
        "vehicle1.jpg"
    )


    result = run_pipeline(
        test_image
    )


    print(
        "\n==================================="
    )

    print(
        "FINAL RESULT"
    )

    print(
        "==================================="
    )

    print(
        result
    )