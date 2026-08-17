from ultralytics import YOLO
import cv2
import easyocr
import re
import os
import gc
from pathlib import Path


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"

BEST_MODEL = MODELS_DIR / "best.pt"

OUTPUT_DIR = BASE_DIR / "outputs"


print("===================================")
print("PlateScout Pipeline")
print("===================================")
print("Project directory:", BASE_DIR)
print("YOLO model:", BEST_MODEL)


# ==================================================
# CHECK MODEL
# ==================================================

if not BEST_MODEL.exists():
    raise FileNotFoundError(
        f"YOLO model not found: {BEST_MODEL}"
    )


# ==================================================
# GLOBAL OBJECTS
# ==================================================

# IMPORTANT:
# Do NOT load YOLO and EasyOCR together.
#
# They will be loaded only when required.
#
# This reduces memory usage on Render.

yolo_model = None
ocr_reader = None


# ==================================================
# LOAD YOLO MODEL
# ==================================================

def get_yolo_model():

    global yolo_model

    if yolo_model is None:

        print("\nLoading YOLO model...")

        yolo_model = YOLO(
            str(BEST_MODEL)
        )

        print("YOLO model loaded.")

    return yolo_model


# ==================================================
# RELEASE YOLO MODEL
# ==================================================

def release_yolo_model():

    global yolo_model

    if yolo_model is not None:

        print("Releasing YOLO model...")

        yolo_model = None

        gc.collect()

        print("YOLO model released.")


# ==================================================
# LOAD OCR
# ==================================================

def get_ocr_reader():

    global ocr_reader

    if ocr_reader is None:

        print("\nLoading EasyOCR...")

        ocr_reader = easyocr.Reader(
            ['en'],
            gpu=False,
            verbose=False
        )

        print("EasyOCR loaded.")

    return ocr_reader


# ==================================================
# RELEASE OCR
# ==================================================

def release_ocr_reader():

    global ocr_reader

    if ocr_reader is not None:

        print("Releasing EasyOCR...")

        ocr_reader = None

        gc.collect()

        print("EasyOCR released.")


# ==================================================
# OCR CLEANING
# ==================================================

def clean_plate_text(text):

    if not text:
        return ""

    text = text.upper()

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

    print("\n===================================")
    print("Starting OCR")
    print("===================================")

    if plate is None or plate.size == 0:

        return None, 0.0


    # ------------------------------------------------
    # Resize
    # ------------------------------------------------

    upscaled = cv2.resize(
        plate,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )


    # ------------------------------------------------
    # Grayscale
    # ------------------------------------------------

    gray = cv2.cvtColor(
        upscaled,
        cv2.COLOR_BGR2GRAY
    )


    # ------------------------------------------------
    # CLAHE
    # ------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)


    # ------------------------------------------------
    # OTSU
    # ------------------------------------------------

    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )


    # ------------------------------------------------
    # Adaptive threshold
    # ------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


    # ------------------------------------------------
    # Output directory
    # ------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # ------------------------------------------------
    # Save preprocessing images
    # ------------------------------------------------

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


    # ------------------------------------------------
    # Load OCR only now
    # ------------------------------------------------

    reader = get_ocr_reader()


    images = [
        ("original", upscaled),
        ("enhanced", enhanced),
        ("otsu", otsu),
        ("adaptive", adaptive)
    ]


    all_results = []


    # ------------------------------------------------
    # OCR
    # ------------------------------------------------

    for name, img in images:

        print(
            f"OCR method: {name}"
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

                if len(result) < 3:
                    continue


                text = result[1]

                confidence = float(
                    result[2]
                )


                cleaned = clean_plate_text(
                    text
                )


                if not cleaned:
                    continue


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


    # ------------------------------------------------
    # Remove large temporary images
    # ------------------------------------------------

    del upscaled
    del gray
    del enhanced
    del otsu
    del adaptive

    gc.collect()


    # ------------------------------------------------
    # No results
    # ------------------------------------------------

    if not all_results:

        return None, 0.0


    # ------------------------------------------------
    # Remove duplicates
    # ------------------------------------------------

    unique_results = {}


    for item in all_results:

        text = item["text"]


        if (
            text not in unique_results
            or
            item["confidence"]
            >
            unique_results[text]["confidence"]
        ):

            unique_results[text] = item


    results = list(
        unique_results.values()
    )


    # ------------------------------------------------
    # Prefer valid Indian plates
    # ------------------------------------------------

    valid_results = [

        item

        for item in results

        if is_valid_plate(
            item["text"]
        )

    ]


    if valid_results:

        best = max(
            valid_results,
            key=lambda x: x["confidence"]
        )

    else:

        best = max(
            results,
            key=lambda x: x["confidence"]
        )


    # ------------------------------------------------
    # Final OCR result
    # ------------------------------------------------

    print("\n===================================")
    print("BEST OCR RESULT")
    print("===================================")

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

    print("\n===================================")
    print("Processing Vehicle")
    print("===================================")

    image_path = Path(image_path)


    if not image_path.is_absolute():

        image_path = (
            BASE_DIR /
            image_path
        )


    print(
        "Image:",
        image_path
    )


    # ------------------------------------------------
    # Read image
    # ------------------------------------------------

    image = cv2.imread(
        str(image_path)
    )


    if image is None:

        return {
            "success": False,
            "error":
                "Could not read image"
        }


    # ------------------------------------------------
    # Resize very large images
    # ------------------------------------------------

    max_width = 1600

    height, width = image.shape[:2]


    if width > max_width:

        scale = (
            max_width /
            width
        )

        new_width = max_width

        new_height = int(
            height * scale
        )


        image = cv2.resize(
            image,
            (
                new_width,
                new_height
            ),
            interpolation=cv2.INTER_AREA
        )


        print(
            "Image resized to:",
            new_width,
            "x",
            new_height
        )


    # ------------------------------------------------
    # Load YOLO
    # ------------------------------------------------

    model = get_yolo_model()


    # ------------------------------------------------
    # YOLO detection
    # ------------------------------------------------

    print("\nRunning YOLO...")


    results = model.predict(
        source=image,
        imgsz=416,
        conf=0.25,
        max_det=1,
        verbose=False,
        device="cpu"
    )


    result = results[0]


    # ------------------------------------------------
    # Check detection
    # ------------------------------------------------

    if len(result.boxes) == 0:

        print(
            "No license plate detected."
        )

        del results
        del result

        release_yolo_model()

        return {
            "success": False,
            "error":
                "No license plate detected"
        }


    print(
        "License plate detected!"
    )


    # ------------------------------------------------
    # Get best detection
    # ------------------------------------------------

    best_box = None

    best_confidence = 0.0


    for box, confidence in zip(
        result.boxes.xyxy,
        result.boxes.conf
    ):

        conf = float(
            confidence.cpu().item()
        )


        if conf > best_confidence:

            best_confidence = conf

            best_box = (
                box.cpu().numpy()
            )


    # ------------------------------------------------
    # Safety check
    # ------------------------------------------------

    if best_box is None:

        del results
        del result

        release_yolo_model()

        return {
            "success": False,
            "error":
                "Could not determine "
                "license plate location"
        }


    # ------------------------------------------------
    # Coordinates
    # ------------------------------------------------

    x1, y1, x2, y2 = map(
        int,
        best_box
    )


    print(
        "Plate coordinates:",
        x1,
        y1,
        x2,
        y2
    )


    # ------------------------------------------------
    # Padding
    # ------------------------------------------------

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


    # ------------------------------------------------
    # Crop plate
    # ------------------------------------------------

    plate = image[
        y1:y2,
        x1:x2
    ]


    if plate.size == 0:

        del results
        del result

        release_yolo_model()

        return {
            "success": False,
            "error":
                "Plate crop failed"
        }


    # ------------------------------------------------
    # Save crop
    # ------------------------------------------------

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
        "Plate cropped successfully."
    )


    # =================================================
    # IMPORTANT MEMORY STEP
    # =================================================
    #
    # YOLO is no longer needed.
    #
    # Release YOLO BEFORE loading EasyOCR.
    #
    # This prevents both large ML models from
    # occupying memory at the same time.
    # =================================================

    del results
    del result
    del model
    del best_box

    gc.collect()

    release_yolo_model()


    # ------------------------------------------------
    # OCR
    # ------------------------------------------------

    plate_text, ocr_confidence = (
        perform_ocr(plate)
    )


    # Release plate/image memory

    del plate
    del image

    gc.collect()


    # ------------------------------------------------
    # OCR failed
    # ------------------------------------------------

    if not plate_text:

        return {
            "success": False,
            "error":
                "No text detected"
        }


    # ------------------------------------------------
    # Validate
    # ------------------------------------------------

    if is_valid_plate(
        plate_text
    ):

        plate_format = "VALID"

    else:

        plate_format = "INVALID"


    # ------------------------------------------------
    # Final result
    # ------------------------------------------------

    print("\n===================================")
    print("FINAL PIPELINE RESULT")
    print("===================================")

    print(
        "Registration:",
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


    print("\n===================================")
    print("FINAL RESULT")
    print("===================================")

    print(result)