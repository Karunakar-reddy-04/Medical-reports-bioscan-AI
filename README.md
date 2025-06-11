# 🧬 BioScan AI – AI-Powered Medical Report Analyzer

BioScan AI is a full-stack healthtech web application that allows users to upload chest X-ray images and receive instant AI-powered diagnostic predictions (e.g., "Pneumonia Likely"). The system supports doctor review, role-based access, report history tracking, and health analytics.

---

## 🚀 Features

- 📤 Upload and analyze chest X-rays using a pretrained AI model (DenseNet121)
- 🔐 User authentication (JWT-based) with **role support** (patient, doctor)
- 📄 View personal report history (patients) or all reports (doctors)
- 💬 Doctor comment system for second opinions
- 📊 Interactive analytics dashboards using `recharts`
- 📧 Email alerts for critical AI findings (e.g., pneumonia)
- 🔁 Real-time prediction simulation (extendable to real CheXNet model)

---

## 🛠 Tech Stack

| Layer        | Technology                         |
|--------------|-------------------------------------|
| Frontend     | React, Material UI, Recharts        |
| Backend      | FastAPI, SQLAlchemy, JWT, Pydantic  |
| AI Model     | PyTorch, Torchvision (DenseNet121)  |
| Database     | SQLite (for local dev)              |
| Email Alerts | aiosmtplib (Gmail SMTP)             |

---

## 📦 Setup Instructions

### 🔧 Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload


💻 Frontend (React)
cd frontend
npm install
npm start
Frontend runs at: http://localhost:3000
Backend runs at: http://localhost:8000

👥 User Roles
| Role    | Access                                                      |
| ------- | ----------------------------------------------------------- |
| Patient | Upload X-rays, view personal report history, receive alerts |
| Doctor  | View all reports, add comments, view dashboard analytics    |


📊 Analytics
Patients: Line chart of past diagnoses

Doctors: Bar chart of report types 

Weekly trend support available via FastAPI endpoints

📬 Email Alerts
If AI predicts "Pneumonia Likely", the system will automatically email the patient with a warning and recommendation to consult a doctor.

🧠 AI Model
Uses DenseNet121 from torchvision

Can be swapped with custom-trained CheXNet model for medical-grade predictions

