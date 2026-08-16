from ultralytics import YOLO

# Load the number plate detection model
model = YOLO("models/best.pt")

# Give the vehicle image to YOLO
results = model("test_images/vehicle1.jpg")

# Save the detected result
for result in results:
    result.save(filename="outputs/detected_plate.jpg")

print("Detection completed!")
print("Result saved in outputs/detected_plate.jpg")