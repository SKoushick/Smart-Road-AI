# Smart Road Infrastructure Monitoring System

> **AI-Powered Civic Complaint & Road Damage Detection Platform**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🚧 Overview

A **smart civic infrastructure monitoring system** that allows citizens to report road damage (potholes, cracks, hazards) via images & location names. The system uses AI-based pothole detection, geolocation mapping, and cloud storage to create a centralized platform for authorities to track and resolve road issues.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🚧 **Citizen Portal** | Upload image + location → get instant AI severity score |
| 🤖 **AI Detection** | CNN (ResNet-18) / OpenCV heuristic with graceful fallback |
| 🗺️ **Interactive Map** | PyDeck 3-D scatter & heatmap with colour-coded markers |
| 🏛️ **Government Panel** | Passkey-protected authority dashboard with inline status updates |
| 📋 **Complaint History** | Searchable, filterable log with CSV export |
| 📊 **Analytics Dashboard** | Plotly charts: trend, severity pie, location bar, resolution gauge |
| ☁️ **AWS S3 Storage** | Image cloud upload (gracefully skipped if not configured) |
| 🗄️ **SQLite Database** | Zero-config local DB — auto-created on first run |

---

## 🏗️ Project Structure

```
smart-road-monitoring/
│
├── app.py                          # Home page & navigation
│
├── pages/
│   ├── 1_user_report.py            # Citizen complaint form
│   ├── 2_government_panel.py       # Authority monitoring panel
│   ├── 3_complaint_history.py      # Full complaint log
│   └── 4_dashboard.py              # Analytics & charts
│
├── models/
│   └── pothole_cnn_model.py        # ResNet-18 CNN architecture
│
├── services/
│   ├── ai_detection_service.py     # Torch → OpenCV → PIL fallback
│   ├── geocoding_service.py        # Nominatim + offline fallback
│   ├── image_processing_service.py # Save, resize, S3 upload
│   └── complaint_service.py        # Full submission pipeline
│
├── database/
│   ├── db_connection.py            # SQLite connection & schema
│   └── complaint_repository.py     # CRUD + analytics queries
│
├── utils/
│   ├── auth_utils.py               # Government panel auth
│   ├── map_utils.py                # PyDeck map builders
│   └── dashboard_utils.py          # Plotly chart factories
│
├── config/
│   └── settings.py                 # All configuration constants
│
├── uploads/temp_images/            # Temporary local image storage
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone / open the project

```bash
cd "Smart Road"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure AWS S3

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=smart-road-images
```

> 💡 If `.env` is not provided, images are stored locally in `uploads/temp_images/`.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** 🎉

---

## 🔐 Government Login Credentials

| Field    | Default Value    |
|----------|-----------------|
| Username | `admin`          |
| Password | `admin123`       |
| Passkey  | `SMARTROAD2024`  |

> Change these in `config/settings.py` or via environment variables.

---

## 🤖 AI Detection

The app uses a **ResNet-18 CNN** for pothole classification with automatic fallback:

```
1. PyTorch + ResNet-18  →  (if torch installed)
2. OpenCV heuristic     →  (if cv2 installed)
3. PIL pixel stats      →  (always available)
```

To use your trained model, place `pothole_weights.pth` in the `models/` folder.

### Severity Thresholds

| Score Range | Severity |
|-------------|----------|
| 0.0 – 0.3   | 🟡 Low   |
| 0.3 – 0.7   | 🟠 Medium |
| 0.7 – 1.0   | 🔴 High  |

---

## 🗺️ Map Marker Colours

| Colour | Meaning         |
|--------|-----------------|
| 🔴 Red    | High severity   |
| 🟠 Orange | Medium severity |
| 🟡 Yellow | Low severity    |
| 🟢 Green  | Resolved        |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly |
| Maps | PyDeck |
| Geocoding | Geopy (Nominatim) |
| AI / ML | PyTorch (ResNet-18) |
| Image Processing | OpenCV + Pillow |
| Cloud Storage | AWS S3 (boto3) |
| Database | SQLite (built-in) |

---

## 📦 Optional Heavy Dependencies

Uncomment in `requirements.txt` if needed:

```bash
# For AI model (GPU accelerated)
pip install torch torchvision

# For AWS S3 image upload
pip install boto3
```

---

## 🔮 Future Enhancements

- Real-time vehicle-mounted camera detection
- Mobile app integration (React Native)
- AI prediction of future road damage risk
- Role-based access control (citizen / officer / admin)
- Integration with municipal repair workflow APIs

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

*Built with ❤️ for Smart City Road Infrastructure Maintenance*
