import easyocr

# Create OCR reader
reader = easyocr.Reader(['en'])

# Read the cropped number plate
result = reader.readtext("outputs/plate_preprocessed.jpg")

print("OCR Result:")

for detection in result:
    text = detection[1]
    confidence = detection[2]

    print("Detected text:", text)
    print("Confidence:", confidence)