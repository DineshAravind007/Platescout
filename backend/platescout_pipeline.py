from ultralytics import YOLO
import cv2
import easyocr
import re
import os


print("===================================")
print("PlateScout Pipeline Started")
print("===================================")


# --------------------------------------------------
# OCR READER
# --------------------------------------------------

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


# --------------------------------------------------
# YOLO MODEL
# --------------------------------------------------

model = YOLO("models/best.pt")


# --------------------------------------------------
# OCR CLEANING
# --------------------------------------------------

def clean_plate_text(text):
    """
    Clean OCR output.
    Keep only English letters and numbers.
    """

    text = text.upper()

    # Remove spaces and special characters
    text = re.sub(r"[^A-Z0-9]", "", text)

    return text


# --------------------------------------------------
# PLATE FORMAT VALIDATION
# --------------------------------------------------

def is_valid_plate(text):
    """
    General Indian vehicle registration format.

    Examples:
    TN87C5106
    KL56Q9009
    KA01AB1234
    """

    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$"

    return re.match(pattern, text) is not None


# --------------------------------------------------
# OCR
# --------------------------------------------------

def perform_ocr(plate):

    print("\nRunning enhanced OCR...")

    # Make sure plate is valid
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
    # Save preprocessing results
    # ----------------------------------------------

    os.makedirs("outputs", exist_ok=True)

    cv2.imwrite(
        "outputs/ocr_original.jpg",
        upscaled
    )

    cv2.imwrite(
        "outputs/ocr_enhanced.jpg",
        enhanced
    )

    cv2.imwrite(
        "outputs/ocr_otsu.jpg",
        otsu
    )

    cv2.imwrite(
        "outputs/ocr_adaptive.jpg",
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

    for name, img in images:

        print(f"\nOCR method: {name}")

        try:

            results = reader.readtext(
                img,
                detail=1,
                paragraph=False,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )

            for result in results:

                if len(result) >= 3:

                    text = result[1]
                    confidence = float(result[2])

                    cleaned = clean_plate_text(text)

                    if cleaned:

                        print(
                            f"Detected: {text} | "
                            f"Cleaned: {cleaned} | "
                            f"Confidence: {confidence:.2f}"
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
                f"OCR error in {name}: {error}"
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
            or result["confidence"]
            > unique_results[text]["confidence"]
        ):

            unique_results[text] = result

    results = list(unique_results.values())

    # ----------------------------------------------
    # Prefer VALID Indian plate formats
    # ----------------------------------------------

    valid_results = [
        result
        for result in results
        if is_valid_plate(result["text"])
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

    print("\n===================================")
    print("BEST OCR RESULT")
    print("===================================")

    print("Plate:", best["text"])
    print("Confidence:", best["confidence"])
    print("Method:", best["method"])

    return best["text"], best["confidence"]


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def run_pipeline(image_path):

    print("\n===================================")
    print("Processing:", image_path)
    print("===================================")

    # ----------------------------------------------
    # Read image
    # ----------------------------------------------

    image = cv2.imread(image_path)

    if image is None:

        print("ERROR: Could not read image.")

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

        print("No license plate detected.")

        return {
            "success": False,
            "error": "No license plate detected"
        }

    print("License plate detected!")

    # ----------------------------------------------
    # Get best detection
    # ----------------------------------------------

    best_box = None
    best_confidence = 0

    for box, confidence in zip(
        result.boxes.xyxy,
        result.boxes.conf
    ):

        conf = float(confidence.cpu().numpy())

        if conf > best_confidence:

            best_confidence = conf
            best_box = box.cpu().numpy()

    # ----------------------------------------------
    # Coordinates
    # ----------------------------------------------

    x1, y1, x2, y2 = map(
        int,
        best_box
    )

    print("Plate coordinates:")
    print(x1, y1, x2, y2)

    # ----------------------------------------------
    # Add small padding
    # ----------------------------------------------

    height, width = image.shape[:2]

    padding = 5

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)

    x2 = min(width, x2 + padding)
    y2 = min(height, y2 + padding)

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
            "error": "Plate crop failed"
        }

    # ----------------------------------------------
    # Save crop
    # ----------------------------------------------

    os.makedirs("outputs", exist_ok=True)

    crop_path = (
        "outputs/pipeline_plate_crop.jpg"
    )

    cv2.imwrite(
        crop_path,
        plate
    )

    print("Plate cropped successfully!")
    print(
        "Saved to:",
        crop_path
    )

    # ----------------------------------------------
    # OCR
    # ----------------------------------------------

    plate_text, ocr_confidence = perform_ocr(
        plate
    )

    # ----------------------------------------------
    # OCR failed
    # ----------------------------------------------

    if not plate_text:

        print("No text detected.")

        return {
            "success": False,
            "error": "No text detected"
        }

    # ----------------------------------------------
    # Validate plate
    # ----------------------------------------------

    if is_valid_plate(plate_text):

        plate_format = "VALID"

    else:

        plate_format = "INVALID"

    print("\n===================================")
    print("FINAL PIPELINE RESULT")
    print("===================================")

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
        "registration_number": plate_text,
        "raw_text": plate_text,
        "ocr_confidence": ocr_confidence,
        "plate_format": plate_format
    }


# --------------------------------------------------
# DIRECT TEST
# --------------------------------------------------

if __name__ == "__main__":

    image_path = "test_images/vehicle1.jpg"

    result = run_pipeline(image_path)

    print("\n===================================")
    print("FINAL RESULT")
    print("===================================")

    print(result)

def process_vehicle_image(image_path):
    return run_pipeline(image_path)