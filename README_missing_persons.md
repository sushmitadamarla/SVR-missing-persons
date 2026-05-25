# 🔍 Smart Visual Recognition for Finding Missing Persons

An AI-powered face recognition system that helps identify and locate missing persons using deep learning and computer vision.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)

---

## 🧠 Overview

This system uses **InsightFace** and **OpenCV** to perform high-accuracy face detection and recognition. Given a reference photo of a missing person, the system can scan images or video feeds and flag potential matches — aiding search and identification efforts.

---

## ✨ Features

- 🖼️ Upload a reference photo of a missing person
- 🔎 Detect and extract faces from images or video frames
- 🤖 Match faces against a registered database using deep embeddings
- 📊 Return similarity scores and match confidence
- 🗃️ Register and manage missing persons in the database

---

## 🛠 Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.x                        |
| Face Recognition | InsightFace (ArcFace model)       |
| Computer Vision  | OpenCV                            |
| Embeddings       | 512-d facial feature vectors      |

---

## ⚙️ How It Works

```
Input Image / Frame
       │
       ▼
┌─────────────────┐
│  Face Detection  │  ◄── OpenCV + InsightFace RetinaFace detector
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  Face Alignment &    │  ◄── Normalizes facial landmarks
│  Preprocessing       │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Feature Extraction  │  ◄── InsightFace ArcFace generates 512-d embedding
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Similarity Search   │  ◄── Cosine similarity against registered embeddings
└────────┬─────────────┘
         │
         ▼
     Match Result
  (Person ID + Score)
```

### Key Concepts

- **InsightFace / ArcFace** — A state-of-the-art face recognition model that maps facial features into a high-dimensional embedding space. Faces of the same person cluster closely together.
- **Cosine Similarity** — Used to measure how close two face embeddings are. A score closer to `1.0` indicates a strong match.
- **OpenCV** — Handles image I/O, frame extraction from video, and pre-processing (resizing, color conversion).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/missing-persons-recognition.git

# Navigate into the project
cd missing-persons-recognition

# Install dependencies
pip install -r requirements.txt
```

### Requirements (`requirements.txt`)

```
insightface
opencv-python
numpy
onnxruntime
```

### Run the App

```bash
python app.py
```

The server will start at `http://localhost:5000`.

---

## 📡 API Documentation

Base URL: `http://localhost:5000/api`

---

### 👤 Register a Missing Person

```http
POST /api/persons/register
```

**Request:** `multipart/form-data`

| Field  | Type   | Description                        |
|--------|--------|------------------------------------|
| `name` | string | Full name of the missing person    |
| `image`| file   | Clear reference photo (JPG/PNG)    |

**Response:** `201 Created`

```json
{
  "id": "abc123",
  "name": "John Doe",
  "message": "Person registered successfully."
}
```

---

### 🔍 Search for a Match

```http
POST /api/search
```

**Request:** `multipart/form-data`

| Field   | Type  | Description                                  |
|---------|-------|----------------------------------------------|
| `image` | file  | Photo or video frame to search within        |

**Response:** `200 OK`

```json
{
  "matches": [
    {
      "person_id": "abc123",
      "name": "John Doe",
      "similarity": 0.91,
      "confidence": "High"
    }
  ]
}
```

> A similarity score above `0.6` is considered a potential match. Above `0.85` is a high-confidence match.

---

### 📋 Get All Registered Persons

```http
GET /api/persons
```

**Response:** `200 OK`

```json
[
  {
    "id": "abc123",
    "name": "John Doe",
    "registered_at": "2024-04-10T08:30:00Z"
  }
]
```

---

### 🗑️ Remove a Registered Person

```http
DELETE /api/persons/{id}
```

**Response:** `200 OK`

```json
{
  "message": "Person removed successfully."
}
```

> Returns `404 Not Found` if the person ID does not exist.

---

## 📁 Project Structure

```
missing-persons-recognition/
├── app.py                   # Entry point
├── requirements.txt
├── api/
│   ├── routes.py            # API endpoint definitions
├── core/
│   ├── detector.py          # Face detection (OpenCV + InsightFace)
│   ├── embedder.py          # Feature extraction (ArcFace)
│   └── matcher.py           # Similarity search logic
├── database/
│   └── persons.py           # Registered persons store
├── utils/
│   └── image_utils.py       # Pre-processing helpers
└── README.md
```

---

## ⚠️ Ethical Notice

This tool is intended **strictly for humanitarian purposes** — to assist in the search and identification of missing persons. Misuse of facial recognition technology for unauthorized surveillance or tracking is prohibited.

---

## 📄 License

This project is for educational/portfolio purposes.
