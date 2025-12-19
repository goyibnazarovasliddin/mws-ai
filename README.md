# SecretSense AI - Advanced Secret Detection Backend System

## Project Overview
SecretSense is an intelligent backend system designed to analyze security scan reports (like Gitleaks or SARIF) and filter out False Positives using a multi-layered approach. It combines static heuristics, Machine Learning (Random Forest), and Large Language Models (OpenAI) to provide high-accuracy secret detection.

## Key Features
1.  **4-Stage Analysis Pipeline**:
    *   **Stage 1 (Parser)**: Normalizes diverse scanner outputs into a unified Finding schema.
    *   **Stage 2 (Rules)**: Fast regex and keyword-based filtering for obvious cases.
    *   **Stage 3 (ML Model)**: A Random Forest classifier trained on entropy and context features.
    *   **Stage 4 (LLM)**: GPT-4o verification for complex, ambiguous "gray area" cases.
2.  **Adaptive Feedback Loop**: The system "re-learns" from users. When you mark a finding as Correct or Incorrect, the system uses that data to retrain the ML model.
3.  **Authentication**: Secure JWT-based authentication with Argon2 password hashing.
4.  **Background Processing**: Uses Celery and Redis to handle large scan reports without blocking the API.

---

## All CLI Commands (Cheat Sheet)

### 1. Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment config
# Edit .env with your OPENAI_API_KEY and SECRET_KEY
cp .env.example .env

# Initialize Database tables
python -m src.scripts.init_db

# Seed initial admin user (admin / admin123)
python -m src.scripts.seed_data
```

### 2. Running the Application
```bash
# Start the API (FastAPI)
uvicorn app.main:app --app-dir src --reload

# Start the Celery Worker (for background analysis)
# Ensure Redis is running first!
celery -A src.app.workers.worker worker --loglevel=info

# Using Docker Compose (Full stack: App, DB, Redis, Worker)
docker-compose up --build
```

### 3. ML Lifecycle & Re-learning
The model improves as it gets more data from you.
```bash
# RETRAIN: Syncs synthetic data with real User Feedback from the DB
# Creates a new versioned .pkl file and updates the active model.
python -m src.app.ml.train

# EVALUATE: Print Accuracy, precision, recall, and Confusion Matrix
python -m src.app.ml.evaluate
```

### 4. Testing & Manual Checks
```bash
# Run all automated tests (Auth, Parser, ML, API)
pytest

# Run a specific benchmark benchmark case (46-50 are complex)
python src/tests/run_case.py 46

# Test the login/register flow via script
python src/tests/test_auth_manual.py
```

---

## Core Logic & Re-learning Mechanism

### The Feedback-Based Learning
One of SecretSense's most powerful features is its **Self-Learning capability**:

1.  **Feedback Capture**: When you submit a verdict via `POST /api/v1/feedback/`, the system stores the finding features and your correction in the `feedbacks` table.
2.  **Hybrid Training**: The `src/app/ml/train.py` script queries the database for all user feedback. It mixes this **high-value real data** with synthetic examples.
3.  **Continuous Improvement**: This allows the model to learn your organization's specific coding patterns (e.g., custom token formats or internal variable naming) that a generic scanner would always miss.
4.  **Automatic Versioning**: Every training run produces a timestamped model file (e.g., `classifier_v_20251219_120000.pkl`), allowing you to track performance growth or rollback if needed.

---

## Project Structure
```
project-root/
├── src/
│   ├── app/
│   │   ├── api/            # API Endpoints (Auth, Analyze, Results, Feedback)
│   │   ├── core/           # Security (JWT, Hashing) & Utilities
│   │   ├── db/             # Database Session & Base models
│   │   ├── ml/             # Machine Learning (Predict, Train, Features, Models)
│   │   ├── models/         # SQLAlchemy Tables & Pydantic Schemas
│   │   ├── services/       # Core Business Logic (Orchestrator, Parser, Rules, LLM)
│   │   ├── workers/        # Celery & Background Tasks
│   ├── scripts/            # DB Init and Seed scripts
│   ├── tests/              # Comprehensive test suite
├── data/                   # Default storage for secretsense.db
├── requirements.txt        # Dependencies
└── .env                    # Secrets & Keys
```

---

## Security Best Practices
*   **JWT Protected**: Every sensitive API call requires an `Authorization: Bearer <token>` header.
*   **Masking**: Findings are stored as snippets, but the system includes utilities to mask secrets in logs.
*   **Password Safety**: Passwords are never stored in plain text; we use `passlib` with Argon2/Bcrypt.

> [!TIP]
> **Performance Note**: The current baseline accuracy is ~95%. This is intentional to simulate real-world overlaps. As you provide real feedback, the precision will trend towards 100% for your specific codebase.

---
*Built for the AI Boostcamp Competition.*
