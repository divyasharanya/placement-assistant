# AI Mock Interview Trainer

A production-grade, AI-native platform that simulates real technical interviews with voice interaction, dynamic DSA challenges, and ATS intelligence.

## 🏗️ Architecture

This project follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│                     http://localhost:3000                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong)                           │
│                       http://localhost:8000                       │
└─────────────────────────────────────────────────────────────────┘
          │              │            │              │           │
          ▼              ▼            ▼              ▼           ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐
   │  Auth    │   │ Resume   │  │Interview │  │   DSA    │  │   AI    │
   │ Service  │   │ Service  │  │ Service  │  │ Service  │  │ Engine  │
   │ :8001    │   │  :8002   │  │  :8003   │  │  :8004   │  │  :8005  │
   └──────────┘   └──────────┘  └──────────┘  └──────────┘  └─────────┘
          │              │            │              │           
          └──────────────┴────────────┴──────────────┘           
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌──────────┐        ┌──────────┐        ┌──────────┐
       │PostgreSQL│        │  Redis   │        │ MongoDB  │
       │  :5432   │        │  :6379   │        │  :27017  │
       └──────────┘        └──────────┘        └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Clone the repository**

2. **Start all services with Docker Compose**
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Access the services**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Auth Service: http://localhost:8001
   - Resume Service: http://localhost:8002
   - Interview Service: http://localhost:8003
   - DSA Service: http://localhost:8004
   - AI Engine: http://localhost:8005
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001

### Manual Setup

1. **Backend Services**
   ```bash
   # Auth Service
   cd backend/auth-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8001

   # Resume Service
   cd backend/resume-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8002

   # Interview Service
   cd backend/interview-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8003

   # DSA Service
   cd backend/dsa-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8004

   # AI Engine
   cd backend/ai-engine
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8005
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📁 Project Structure

```
placement_assisstant/
├── backend/
│   ├── auth-service/           # Authentication microservice
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── resume-service/         # Resume parsing & ATS analysis
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── interview-service/       # Interview session management
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── dsa-service/            # Code execution & evaluation
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── ai-engine/              # AI-powered features
│       ├── main.py
│       ├── Dockerfile
│       └── requirements.txt
├── frontend/                    # Next.js web application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── ui/
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── stores/
│   │   └── index.ts
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.js
├── database/
│   └── models.py               # SQLAlchemy & Pydantic models
├── docker/
│   ├── docker-compose.yml
│   └── kong.yml                # API Gateway config
├── infrastructure/
│   ├── kubernetes/              # K8s manifests
│   │   ├── namespace.yaml
│   │   ├── auth-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   └── ingress.yaml
│   ├── terraform/              # AWS infrastructure
│   │   └── main.tf
│   ├── monitoring/              # Prometheus config
│   │   └── prometheus.yml
│   └── github-actions.yml      # CI/CD pipeline
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql+asyncpg://user:pass@localhost:5432/aimock |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `SECRET_KEY` | JWT signing key | change-me-in-production |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

## 📝 API Endpoints

### Authentication (`/v1/auth`)
- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login
- `POST /v1/auth/refresh` - Refresh token
- `GET /v1/auth/me` - Get current user

### Resume (`/v1/resumes`)
- `POST /v1/resumes` - Create resume
- `GET /v1/resumes/{id}` - Get resume
- `POST /v1/resumes/{id}/parse` - Parse resume
- `POST /v1/resumes/{id}/analyze` - Run ATS analysis

### Interview (`/v1/interviews`)
- `POST /v1/interviews` - Create interview
- `GET /v1/interviews/{id}` - Get interview
- `POST /v1/interviews/{id}/start` - Start interview
- `POST /v1/interviews/{id}/answer` - Submit answer
- `POST /v1/interviews/{id}/feedback` - Get feedback

### DSA (`/v1/dsa`)
- `GET /v1/dsa/problems` - List problems
- `GET /v1/dsa/problems/{slug}` - Get problem
- `POST /v1/dsa/problems/{slug}/submit` - Submit solution

### AI Engine (`/v1/ai`)
- `POST /v1/ai/interview-plan` - Generate interview plan
- `POST /v1/ai/analyze` - Analyze response
- `POST /v1/ai/feedback` - Generate feedback

## 🧪 Testing

```bash
# Backend tests
cd backend/auth-service
pytest

# Frontend tests
cd frontend
npm run test
```

## 🚀 Deployment

### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/

# Check deployment status
kubectl get pods -n aimock
```

### AWS EKS

```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Configure kubectl
aws eks update-kubeconfig --name aimock-cluster

# Deploy application
kubectl apply -f ../kubernetes/
```

## 📈 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## 🔐 Security

- JWT-based authentication with refresh tokens
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM
- CORS configuration

## 📄 License

MIT License - see LICENSE file for details.
# placement-assistant
