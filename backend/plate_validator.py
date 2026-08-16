import re


def clean_plate(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def validate_plate(plate):
    # General Indian registration format:
    # 2 letters + 1-2 digits + 1-3 letters + 1-4 digits
    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$"

    return bool(re.match(pattern, plate))


# OCR result
ocr_text = "KL 56 Q 9009"

# Clean
plate_number = clean_plate(ocr_text)

# Validate
is_valid = validate_plate(plate_number)

print("Original OCR:", ocr_text)
print("Cleaned Plate:", plate_number)
print("Valid Indian plate format:", is_valid)