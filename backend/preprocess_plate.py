import cv2

# Read the cropped number plate
image = cv2.imread("outputs/plate_crop.jpg")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Increase the size of the plate
upscaled = cv2.resize(
    gray,
    None,
    fx=3,
    fy=3,
    interpolation=cv2.INTER_CUBIC
)

# Reduce small noise
blurred = cv2.GaussianBlur(upscaled, (3, 3), 0)

# Improve contrast using thresholding
_, threshold = cv2.threshold(
    blurred,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)

# Save the processed plate
cv2.imwrite("outputs/plate_preprocessed.jpg", threshold)

print("Plate preprocessing completed!")
print("Saved to: outputs/plate_preprocessed.jpg")