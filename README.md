# SecretSense AI - Advanced Secret Detection Backend System

## Project Overview
SecretSense is an intelligent backend system designed to analyze security scan reports (like Gitleaks SARIF) and filter out False Positives using a multi-layered approach. It combines static heuristics, Machine Learning (Random Forest), and Large Language Models (OpenAI) to provide high-accuracy secret detection.

## Key Features
1.  **3-Layer Analysis Pipeline**:
    *   **Layer 1 (Rules)**: Fast regex and keyword-based filtering.
    *   **Layer 2 (ML Model)**: A Random Forest classifier trained on entropy and context features.
    *   **Layer 3 (LLM)**: OpenAI GPT-4o verification for complex, ambiguous cases.
2.  **Feedback Loop & Retraining**: Users can mark findings as "False Positive" or "True Positive". The system saves this feedback and can retrain its ML model to improve over time.
3.  **Authentication**: Secure JWT-based authentication with Argon2 password hashing.
4.  **REST API**: Fully documented FastAPI endpoints.

## Project Structure
```
project-root/
├── src/
│   ├── app/
│   │   ├── api/            # API Endpoints (Auth, Analyze, Results, Feedback)
│   │   ├── core/           # Security & Config (JWT, Hashing)
│   │   ├── db/             # Database Session & Base models
│   │   ├── ml/             # Machine Learning (Predict, Train, Features)
│   │   ├── models/         # SQLAlchemy Tables & Pydantic Schemas
│   │   ├── services/       # Business Logic (Parser, Rules, LLM Client)
│   ├── tests/              # Test Scripts (Benchmarks, Auth Tests)
├── data/                   # SQLite Database (secretsense.db)
├── requirements.txt        # Python Dependencies
└── .env                    # Secrets (API Keys, DB URL)
```

## Installation & Setup

1.  **Prerequisites**: Python 3.9+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**:
    Create a `.env` file in `project-root`:
    ```ini
    DATABASE_URL=sqlite:///./data/secretsense.db
    SECRET_KEY=your_jwt_secret_key
    OPENAI_API_KEY=sk-proj-...
    ```

## How to Run
Start the development server:
```bash
python -m uvicorn src.app.main:app --reload
```
Access Swagger UI at: `http://localhost:8000/docs`

## Core Logic Explained

### The Analysis Funnel (`src/app/services/ml_pipeline.py`)
1.  **Parsing**: Converts SARIF/JSON input into a standardized `Finding` object.
2.  **Rule Filter**: Checks filenames (`test_`, `mock_`) and keywords (`example`, `dummy`). If matched -> marked as False Positive.
3.  **ML Inference**: Extracts features (Entropy, String Length, etc.) and asks `classifier.pkl` for a probability score.
4.  **LLM Verification**: If the ML model is unsure (confidence between 0.4 and 0.7), it sends the snippet to GPT-4o for a "human-like" verdict.

## Data Lifecycle & Learning

### 1. where Feedback Goes
When a user submits feedback via `/api/v1/feedback/` (or via the interactive test script), the system stores:
*   The **Finding ID** (what snippet was found).
*   The **User's Verdict** (whether they confirmed it as True Positive or False Positive).
*   **Storage**: This data is saved in the **`feedbacks`** table in the SQLite database (`data/secretsense.db`).

### 2. How the ML Model Trains
The training script (`src/app/ml/train.py`) uses a **Hybrid Dataset**:
1.  **Synthetic Data**: It generates 1,000+ synthetic examples of fake secrets (stubs, placeholders) and real secrets (high entropy strings) to ensure a baseline understanding.
2.  **Real User Feedback**: It connects to the database, pulls all labeled feedback, extracts features (Entropy, Length, Keywords) from the referenced findings, and mixes them into the training set.

### 3. Future of the Model
*   **Continuous Improvement**: As more users verify findings, the "Feedback" dataset grows.
*   **Adaptive Security**: The model eventually learns organization-specific patterns (e.g., custom token formats or internal variable naming conventions) that generic rules might miss.
*   **Automated Re-training**: In a production environment, `train.py` can be triggered automatically (e.g., nightly via Celery) to produce a fresh `classifier.pkl`.

## API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/v1/auth/register` | Register a new user |
| **POST** | `/api/v1/auth/login` | Login (returns JWT Token) |
| **POST** | `/api/v1/analyze` | Submit a scan report (SARIF/JSON) |
| **GET** | `/api/v1/results/{id}` | Get analysis results & AI verdicts |
| **POST** | `/api/v1/feedback/` | Submit User Feedback (Correct/Incorrect) |

## Testing & Validation

**1. Benchmark Suite**
Run specific test cases to verify the pipeline:
```bash
python src/tests/run_case.py 46
```
*   Cases 1-15: Rule-based checks.
*   Cases 16-30: Pure ML checks.
*   Cases 31-45: LLM-required checks.
*   Cases 46-50: Complex multi-finding reports.

**2. Manual Auth Test**
Test the login/register flow:
```bash
python src/tests/test_auth_manual.py
```

**3. Retraining**
Incorporate feedback into the model:
```bash
python src/app/ml/train.py
```

---
*Built for the AI Boostcamp Competition.*
