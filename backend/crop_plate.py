from ultralytics import YOLO
import cv2

# Load the license plate model
model = YOLO("models/best.pt")

# Read the vehicle image
image = cv2.imread("test_images/vehicle1.jpg")

# Detect the number plate
results = model(image)

# Get the first detection result
result = results[0]

if len(result.boxes) == 0:
    print("No license plate detected.")

else:
    # Get the first detected plate coordinates
    box = result.boxes.xyxy[0].cpu().numpy()

    x1, y1, x2, y2 = map(int, box)

    # Crop the plate
    plate = image[y1:y2, x1:x2]

    # Save the cropped plate
    cv2.imwrite("outputs/plate_crop.jpg", plate)

    print("License plate cropped successfully!")
    print("Saved to: outputs/plate_crop.jpg")