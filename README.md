# PlateScout

## Vehicle Intelligence & License Plate Verification System

PlateScout is an AI-powered Progressive Web App (PWA) that analyzes
vehicle images, detects license plates, extracts registration numbers
using OCR, and retrieves vehicle information from a local SQLite
database.

The project is designed as a hackathon/demo solution for demonstrating
an end-to-end vehicle verification workflow.

> **Important:** The current vehicle information database contains
> clearly labeled demo/test records. It is not a live RTO/Vahan database
> and must not be presented as real-time government verification.

------------------------------------------------------------------------

## 1. Key Features

-   Vehicle image upload from the device
-   Camera capture support
-   License plate detection using YOLO
-   License plate text extraction using EasyOCR
-   OCR confidence display
-   Indian vehicle registration format validation
-   Vehicle information lookup using SQLite
-   Vehicle status cards for:
    -   Registration
    -   Insurance
    -   Fitness
    -   Challans
    -   Vehicle type
    -   Fuel type
-   Detailed vehicle information section
-   Scan another vehicle option
-   Responsive web interface
-   Progressive Web App (PWA) support
-   Backend API using Flask
-   Backend deployment support using Render

------------------------------------------------------------------------

## 2. Project Workflow

``` text
Vehicle Image
     |
     v
React / PWA Frontend
     |
     v
Flask Backend
     |
     v
YOLO License Plate Detection
     |
     v
License Plate Cropping
     |
     v
EasyOCR
     |
     v
Registration Number
     |
     v
SQLite Vehicle Database
     |
     v
Vehicle Information
     |
     v
React Results Screen
```

Example:

``` text
Vehicle Image
     ↓
DL7CQ1939 detected
     ↓
SQLite lookup
     ↓
Hyundai Creta
SUV
Diesel
Registration: Active
Insurance: Valid
Fitness: Valid
Challans: 2
```

------------------------------------------------------------------------

## 3. Technology Stack

### Frontend

-   React
-   Vite
-   JavaScript
-   HTML
-   CSS
-   Progressive Web App (PWA)

### Backend

-   Python
-   Flask
-   YOLO
-   EasyOCR
-   OpenCV
-   SQLite

### Deployment

-   GitHub
-   Render

------------------------------------------------------------------------

## 4. Project Structure

``` text
PlateScout/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── vehicle_api.py
│   ├── vehicles.db
│   ├── models/
│   │   └── best.pt
│   ├── temp/
│   └── ...
│
├── test_images/
│
└── README.md
```

The exact filenames may vary depending on the current project version.

------------------------------------------------------------------------

# 5. Requirements

Make sure the following are installed:

-   Python 3.x
-   Node.js
-   npm
-   Git

A Python virtual environment is recommended for the backend.

------------------------------------------------------------------------

# 6. Backend Setup

Open a terminal and navigate to the backend:

``` powershell
cd E:\PlateScout\backend
```

Create a virtual environment if one does not already exist:

``` powershell
python -m venv venv
```

Activate it:

``` powershell
venv\Scripts\activate
```

Install the required Python packages:

``` powershell
pip install -r requirements.txt
```

If the project does not contain a `requirements.txt`, install the
packages used by the backend environment, including Flask, OpenCV,
EasyOCR, Ultralytics/YOLO, and their dependencies.

------------------------------------------------------------------------

# 7. Initialize the Database

PlateScout uses SQLite.

The database file is:

``` text
backend/vehicles.db
```

It is created automatically by `database.py`.

Run:

``` powershell
cd E:\PlateScout\backend
python database.py
```

You should see output similar to:

``` text
Creating database...
Adding demo vehicle records...
Database ready!
Database location: E:\PlateScout\backend\vehicles.db
```

The current demo database contains records such as:

  Registration   Vehicle               Type        Fuel
  -------------- --------------------- ----------- --------
  DL7CQ1939      Hyundai Creta         SUV         Diesel
  TN87C5106      Maruti Suzuki Swift   Hatchback   Petrol
  KL56Q9009      Honda City            Sedan       Petrol
  KA01AB1234     Tata Nexon            SUV         Petrol
  MH12DE3456     Toyota Etios          Sedan       Diesel
  TN38AB1234     Hyundai i20           Hatchback   Petrol
  AP09XY5678     Kia Seltos            SUV         Diesel
  KL07MN2468     Maruti Suzuki Ciaz    Sedan       Petrol

These are **demo/test records** created for the project demonstration.

------------------------------------------------------------------------

# 8. Start the Backend

From the backend directory:

``` powershell
cd E:\PlateScout\backend
venv\Scripts\activate
python app.py
```

The Flask server should start on the configured local port.

The primary analysis endpoint is:

``` text
POST /api/analyze
```

The frontend sends the selected vehicle image to this endpoint.

------------------------------------------------------------------------

# 9. Start the Frontend

Open another terminal.

Navigate to the frontend:

``` powershell
cd E:\PlateScout\frontend
```

Install dependencies if required:

``` powershell
npm install
```

Start the Vite development server:

``` powershell
npm run dev
```

Vite will provide a local URL, normally similar to:

``` text
http://localhost:5173
```

Open that URL in the browser.

------------------------------------------------------------------------

# 10. How to Use PlateScout

### Step 1 --- Select an image

Use:

-   **Capture Photo** to capture an image using the camera
-   **Choose Image** to select an existing image

### Step 2 --- Analyze

Click:

``` text
Analyze Vehicle
```

### Step 3 --- License plate detection

The backend uses YOLO to locate the license plate.

### Step 4 --- OCR

The detected plate is cropped and processed using EasyOCR.

Example:

``` text
DL7CQ1939
```

### Step 5 --- Database lookup

The extracted registration number is searched in the SQLite database.

### Step 6 --- Display results

If a matching demo record exists, PlateScout displays the available
vehicle information.

------------------------------------------------------------------------

# 11. Example API Response

For a matching demo record, the backend can return data in this
structure:

``` json
{
  "success": true,
  "registration_number": "DL7CQ1939",
  "raw_text": "DL7CQ1939",
  "ocr_confidence": 0.6494,
  "plate_format": "VALID",
  "vehicle_information": {
    "registration_number": "DL7CQ1939",
    "vehicle_type": "SUV",
    "manufacturer": "Hyundai",
    "model": "Creta",
    "fuel_type": "Diesel",
    "registration_status": "Active",
    "insurance_status": "Valid",
    "fitness_status": "Valid",
    "challan_count": 2,
    "source": "PlateScout Demo Database",
    "data_type": "DEMO",
    "last_updated": "2026-08-19"
  }
}
```

------------------------------------------------------------------------

# 12. OCR and Confidence

PlateScout runs OCR on the detected license plate.

The application displays the OCR confidence as a percentage.

For example:

``` text
OCR Confidence: 64.9%
```

The OCR stage may use multiple image-processing methods to improve
recognition, including:

-   Original image
-   Enhanced image
-   Otsu thresholding
-   Adaptive thresholding

The final recognized registration number is selected by the backend's
OCR processing logic.

------------------------------------------------------------------------

# 13. Database Architecture

PlateScout currently uses SQLite because it is simple, lightweight, and
suitable for the hackathon/demo environment.

The database contains:

``` text
vehicles
│
├── registration_number
├── vehicle_type
├── manufacturer
├── model
├── fuel_type
├── registration_status
├── insurance_status
├── fitness_status
├── challan_count
├── source
├── data_type
└── last_updated
```

The database is accessed through:

``` text
database.py
```

The vehicle lookup layer is handled through:

``` text
vehicle_api.py
```

This separation makes it easier to replace the demo database with an
authorized external vehicle-data provider in a future version.

------------------------------------------------------------------------

# 14. Important Data Limitation

The current version does **not** directly access live government
RTO/Vahan records.

The SQLite records are:

``` text
Source: PlateScout Demo Database
Data Type: DEMO
```

Therefore:

-   Vehicle information should be treated as demonstration data.
-   The application must not claim that demo records are current
    government records.
-   Production deployment would require an authorized vehicle-data
    API/provider and appropriate permissions.

------------------------------------------------------------------------

# 15. Error Handling

PlateScout handles common cases such as:

-   No image selected
-   Backend unavailable
-   Invalid API response
-   License plate not detected
-   OCR unable to identify a registration number
-   Registration number not found in the demo database

A future version can provide a dedicated UI state for:

``` text
Vehicle information not found
```

while still displaying the successfully detected registration number.

------------------------------------------------------------------------

# 16. Deployment

The backend can be deployed using Render.

The frontend can be hosted using a suitable static hosting platform.

For production deployment:

1.  Push the project to GitHub.
2.  Deploy the backend.
3.  Configure the frontend API URL.
4.  Build the React application.
5.  Deploy the frontend.
6.  Test the complete image → OCR → database/API workflow.

The free Render instance may sleep after inactivity, which can cause a
delay when the backend receives the first request.

------------------------------------------------------------------------

# 17. Security Notes

Do not commit secrets or private API keys to GitHub.

If an external API is integrated in the future, store credentials using
environment variables.

Example:

``` text
API_KEY=your_secret_key
```

Do not hard-code private keys inside:

``` text
App.jsx
database.py
vehicle_api.py
```

or other source files.

------------------------------------------------------------------------

# 18. Future Enhancements

Possible future improvements include:

-   Integration with an authorized live vehicle-data API
-   Real-time RTO/vehicle verification
-   Improved OCR accuracy
-   Multiple plate detection
-   Vehicle make/model recognition using computer vision
-   User authentication
-   Search history
-   Cloud database
-   Admin dashboard
-   Analytics
-   Better mobile PWA support
-   Offline functionality
-   Production-grade security and monitoring

------------------------------------------------------------------------

# 19. Hackathon Deliverables

The project submission includes:

1.  **Working PWA**
    -   Hosted link or local demonstration
2.  **Source Code**
    -   GitHub repository
3.  **README**
    -   Setup instructions and project features
4.  **Demo Video**
    -   2--3 minute demonstration
5.  **Presentation**
    -   Recommended 8--10 slides

------------------------------------------------------------------------

# 20. Quick Start

### Terminal 1 --- Backend

``` powershell
cd E:\PlateScout\backend
venv\Scripts\activate
python database.py
python app.py
```

### Terminal 2 --- Frontend

``` powershell
cd E:\PlateScout\frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

------------------------------------------------------------------------

# 21. Project Summary

PlateScout demonstrates an end-to-end AI-assisted vehicle verification
workflow:

``` text
Capture
   ↓
Detect
   ↓
Read
   ↓
Lookup
   ↓
Verify
   ↓
Display
```

The system combines computer vision, OCR, a Flask API, SQLite database
storage, and a React PWA interface into a single vehicle intelligence
application.

------------------------------------------------------------------------

## License

This project was developed for educational, demonstration, and hackathon
purposes.
