# AI Detection Evidence Manager

**AI Detection Evidence Manager** is a secure, web-based platform built to track, store, and manage digital evidence for AI-related investigations. It provides authorized personnel with a streamlined interface to upload evidence files, categorize them by severity and status, and generate professional custody reports — all backed by a lightweight SQLite database and served via FastAPI.

🌐 **Live Demo**: [https://ai-detection-evidence-manager.onrender.com](https://ai-detection-evidence-manager.onrender.com)

---

## ✨ Features

- **Evidence Upload** — Upload any file as digital evidence linked to a specific Case ID, with metadata including description, custodian name, category, severity, and investigation status.
- **Evidence Dashboard** — View all logged evidence in a sortable table with live statistics (total items, critical alerts, secured items, unique cases).
- **Severity Tracking** — Classify evidence as `Low`, `Medium`, `High`, or `Critical`.
- **Status Management** — Track evidence through statuses: `Under Investigation`, `Secured`, `Archived`, `Pending Review`.
- **Evidence Deletion** — Remove evidence records and their associated files from disk in one action.
- **PDF Report Generation** — Generate and download a formatted **Digital Evidence Custody Report** with all logged evidence details.
- **File Serving** — Uploaded files are directly accessible via a static file endpoint.
- **Auto DB Migration** — Safely adds new columns to existing databases on startup without data loss.

---

## 🛠️ Technology Stack

| Layer          | Technology                           |
|----------------|--------------------------------------|
| Backend        | Python 3, FastAPI                    |
| Server         | Uvicorn (ASGI)                       |
| Templating     | Jinja2                               |
| Database       | SQLite3                              |
| Frontend       | HTML, CSS (Jinja2 templates)         |
| Reporting      | FPDF2 (PDF generation)               |
| Version Control| Git & GitHub                         |

---

## 📁 Project Structure

```
AI-Detection-Evidence-Manager/
├── main.py              # FastAPI app — routes, DB logic, PDF generation
├── templates/
│   └── index.html       # Main UI template (Jinja2)
├── uploads/             # Uploaded evidence files (git-ignored)
├── evidence.db          # SQLite database (git-ignored)
├── .gitignore
└── README.md
```

---

## 🚀 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/yashaswini116/AI-Detection-Evidence-Manager.git
cd AI-Detection-Evidence-Manager
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn fpdf2 jinja2 python-multipart
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

Open your browser and navigate to **http://127.0.0.1:8000**

---

## 📡 API Endpoints

| Method   | Endpoint              | Description                          |
|----------|-----------------------|--------------------------------------|
| `GET`    | `/`                   | Renders the main evidence dashboard  |
| `POST`   | `/upload`             | Upload a new evidence file           |
| `DELETE` | `/evidence/{id}`      | Delete an evidence record by ID      |
| `GET`    | `/report`             | Download the PDF custody report      |
| `GET`    | `/uploads/{filename}` | Serve an uploaded file directly      |

---

## 📋 Evidence Fields

When uploading evidence, the following fields are captured:

| Field         | Description                          | Example                        |
|---------------|--------------------------------------|--------------------------------|
| `case_id`     | Unique identifier for the case       | `CASE-2024-001`                |
| `description` | Brief description of the evidence    | `Screenshot of phishing email` |
| `staff_name`  | Name of the custodian uploading      | `Jane Doe`                     |
| `category`    | Type of evidence                     | `Network Log`, `Screenshot`    |
| `severity`    | Risk level                           | `Low / Medium / High / Critical`|
| `status`      | Current investigation status         | `Under Investigation`          |

---

## 📄 License

This project is for academic and investigative use. All rights reserved © 2024 Yashaswini.
