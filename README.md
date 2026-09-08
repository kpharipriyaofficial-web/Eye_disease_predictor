# 👁️ Eye Disease Predictor

### AI-Powered Eye Disease Classification System

An end-to-end machine learning web application that analyzes eye images and predicts one of four classes:

- Cataracts
- Glaucoma
- Normal
- Uveitis

The system combines a **PyTorch-based Convolutional Neural Network (CNN)** with a **FastAPI backend**, **MongoDB database**, and a modern **React + Vite frontend**.

> ⚠️ This project is intended for educational and research purposes and should not be used as a substitute for professional medical diagnosis.

---

## ✨ Features

- 🧠 Deep learning-based eye disease classification
- 📷 Upload an eye image for prediction
- 📊 Prediction confidence score
- ⚡ Fast image inference using PyTorch
- 🔐 User authentication
- 🗃️ Prediction history
- ☁️ MongoDB-based data storage
- 🌐 REST API using FastAPI
- 💻 Modern React frontend
- 📱 Responsive user interface
- 🔄 Frontend ↔ Backend ↔ ML integration
- 🐳 Docker support for backend deployment

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     React + Vite    │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                               │ HTTP / REST API
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │       Backend       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │     Auth    │  │ ML Predictor│  │   History   │
       │   Service   │  │   Service   │  │   Service   │
       └─────────────┘  └──────┬──────┘  └──────┬──────┘
                               │                 │
                               ▼                 ▼
                        ┌─────────────┐   ┌─────────────┐
                        │ PyTorch CNN │   │   MongoDB   │
                        │ Model       │   │   Database  │
                        └─────────────┘   └─────────────┘
