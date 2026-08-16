import { useRef, useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError("");
  };

  const openGallery = () => {
    fileInputRef.current?.click();
  };

  const openCamera = () => {
    cameraInputRef.current?.click();
  };

  const analyzeVehicle = async () => {
    if (!selectedFile) {
      setError("Please select or capture a vehicle image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const API_URL = `http://${window.location.hostname}:5000`;

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Unable to analyze the vehicle.");
      }

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to PlateScout backend. Make sure Flask is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const scanAnotherVehicle = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    if (cameraInputRef.current) {
      cameraInputRef.current.value = "";
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const vehicleInfo = result?.vehicle_information || {};

  const confidence = result?.ocr_confidence
    ? `${(Number(result.ocr_confidence) * 100).toFixed(1)}%`
    : "—";

  return (
    <div className="app">

      {/* =====================================
          HEADER
      ====================================== */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">🚘</div>

          <div className="brand-text">
            <div className="brand-name">
              PLATE<span>SCOUT</span>
            </div>

            <div className="brand-tagline">
              VEHICLE INTELLIGENCE
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>


      {/* =====================================
          MAIN
      ====================================== */}
      <main className="main-container">

        {/* HERO */}
        <section className="hero">

          <div className="hero-content">

            <div className="hero-badge">
              AI-POWERED VEHICLE VERIFICATION
            </div>

            <h1>
              Know Your Vehicle.
              <br />
              <span>Before You Move.</span>
            </h1>

            <p>
              Capture a vehicle image and let PlateScout detect the
              registration plate, read the number and verify important
              vehicle information.
            </p>

          </div>

          <div className="hero-visual">
            <div className="scan-ring ring-one"></div>
            <div className="scan-ring ring-two"></div>
            <div className="scan-ring ring-three"></div>

            <div className="hero-car">
              🚘
            </div>
          </div>

        </section>


        {/* =====================================
            SCANNER
        ====================================== */}
        <section className="scanner-section">

          <div className="section-heading">

            <div>
              <div className="eyebrow">
                VEHICLE SCANNER
              </div>

              <h2>Scan a Vehicle</h2>

              <p>
                Capture a photo or select an existing vehicle image.
              </p>
            </div>

            <div className="ai-ready">
              <span></span>
              AI READY
            </div>

          </div>


          {/* IMAGE PREVIEW */}
          <div className={`image-box ${preview ? "has-image" : ""}`}>

            {preview ? (
              <>
                <img
                  src={preview}
                  alt="Selected vehicle"
                />

                <div className="image-overlay">

                  <div className="file-name">
                    {selectedFile?.name}
                  </div>

                  <button
                    className="change-button"
                    onClick={openGallery}
                  >
                    Change
                  </button>

                </div>
              </>
            ) : (
              <div className="empty-image">

                <div className="empty-icon">
                  🚘
                </div>

                <h3>No vehicle image selected</h3>

                <p>
                  Capture a photo or choose one from your device.
                </p>

              </div>
            )}

          </div>


          {/* HIDDEN INPUTS */}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            hidden
          />

          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            hidden
          />


          {/* ACTION BUTTONS */}
          <div className="scanner-actions">

            <button
              className="secondary-button"
              onClick={openCamera}
            >
              📷 Capture Photo
            </button>

            <button
              className="secondary-button"
              onClick={openGallery}
            >
              🖼️ Choose Image
            </button>

            <button
              className="analyze-button"
              onClick={analyzeVehicle}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>✦ Analyze Vehicle</>
              )}
            </button>

          </div>


          {/* ERROR */}
          {error && (
            <div className="error-box">
              ⚠️ {error}
            </div>
          )}

        </section>


        {/* =====================================
            RESULTS
        ====================================== */}
        {result && (
          <section className="results-section">

            <div className="section-heading result-heading">

              <div>
                <div className="eyebrow">
                  VERIFICATION
                </div>

                <h2>Vehicle Status</h2>
              </div>

              <div className="scan-complete">
                <span></span>
                Scan Complete
              </div>

            </div>


            {/* MAIN PLATE RESULT */}
            <div className="plate-result">

              <div className="plate-icon">
                #
              </div>

              <div className="plate-center">

                <div className="small-label">
                  DETECTED REGISTRATION
                </div>

                <div className="plate-number">
                  {result.registration_number || "Unknown"}
                </div>

              </div>

              <div className="confidence">

                <div className="small-label">
                  OCR CONFIDENCE
                </div>

                <strong>{confidence}</strong>

              </div>

            </div>


            {/* VALIDATION */}
            <div className="format-status">
              PLATE FORMAT:
              <strong
                className={
                  result.plate_format === "VALID"
                    ? "valid"
                    : "invalid"
                }
              >
                {result.plate_format || "UNKNOWN"}
              </strong>
            </div>


            {/* STATUS CARDS */}
            <div className="status-grid">

              <InfoCard
                icon="✓"
                label="Registration"
                value={vehicleInfo.registration_status}
                description="Registration verified"
              />

              <InfoCard
                icon="✓"
                label="Insurance"
                value={vehicleInfo.insurance_status}
                description="Insurance status checked"
              />

              <InfoCard
                icon="✓"
                label="Fitness"
                value={vehicleInfo.fitness_status}
                description="Fitness status checked"
              />

              <InfoCard
                icon="!"
                label="Challans"
                value={vehicleInfo.challan_count ?? 0}
                description="Challan records checked"
              />

              <InfoCard
                icon="🚘"
                label="Vehicle Type"
                value={vehicleInfo.vehicle_type}
                description="Vehicle identified"
              />

              <InfoCard
                icon="⛽"
                label="Fuel Type"
                value={vehicleInfo.fuel_type}
                description="Fuel information available"
              />

            </div>


            {/* VEHICLE INFORMATION */}
            <div className="vehicle-info-section">

              <div className="eyebrow">
                VERIFIED VEHICLE
              </div>

              <h2>Vehicle Information</h2>

              <div className="verified-badge">
                ✓ VERIFIED
              </div>

              <div className="details-card">

                <DetailRow
                  label="Registration Number"
                  value={
                    vehicleInfo.registration_number ||
                    result.registration_number
                  }
                />

                <DetailRow
                  label="Vehicle Type"
                  value={vehicleInfo.vehicle_type}
                />

                <DetailRow
                  label="Fuel Type"
                  value={vehicleInfo.fuel_type}
                />

                <DetailRow
                  label="Registration Status"
                  value={vehicleInfo.registration_status}
                />

                <DetailRow
                  label="Insurance Status"
                  value={vehicleInfo.insurance_status}
                />

                <DetailRow
                  label="Fitness Status"
                  value={vehicleInfo.fitness_status}
                />

                <DetailRow
                  label="Challan Count"
                  value={vehicleInfo.challan_count ?? 0}
                />

              </div>

            </div>


            {/* OCR INFORMATION */}
            <div className="ocr-result">

              <span>
                OCR DETECTION
              </span>

              <strong>
                {result.registration_number}
              </strong>

            </div>


            {/* SCAN AGAIN */}
            <button
              className="scan-again"
              onClick={scanAnotherVehicle}
            >
              ↻ Scan Another Vehicle
            </button>

          </section>
        )}


        {/* =====================================
            HOW IT WORKS
        ====================================== */}
        {!result && (
          <section className="how-section">

            <div className="eyebrow">
              HOW IT WORKS
            </div>

            <h2>
              From Image to Insight
            </h2>

            <div className="steps">

              <Step
                number="01"
                title="Capture"
                text="Take a vehicle photo using your phone camera."
              />

              <Step
                number="02"
                title="Detect"
                text="AI identifies the vehicle registration plate."
              />

              <Step
                number="03"
                title="Verify"
                text="OCR reads the plate and checks vehicle data."
              />

            </div>

          </section>
        )}

      </main>


      {/* FOOTER */}
      <footer>
        <strong>PLATESCOUT</strong>
        <span>Vehicle Intelligence Platform</span>
      </footer>

    </div>
  );
}


/* ==========================================
   INFO CARD
========================================== */

function InfoCard({
  icon,
  label,
  value,
  description,
}) {
  return (
    <div className="info-card">

      <div className="card-top">

        <div className="card-icon">
          {icon}
        </div>

        <span>
          {label}
        </span>

      </div>

      <strong>
        {value || "Unknown"}
      </strong>

      <small>
        {description}
      </small>

    </div>
  );
}


/* ==========================================
   DETAIL ROW
========================================== */

function DetailRow({
  label,
  value,
}) {
  return (
    <div className="detail-row">

      <span>
        {label}
      </span>

      <strong>
        {value || "Unknown"}
      </strong>

    </div>
  );
}


/* ==========================================
   STEP
========================================== */

function Step({
  number,
  title,
  text,
}) {
  return (
    <div className="step">

      <div className="step-number">
        {number}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}


export default App;