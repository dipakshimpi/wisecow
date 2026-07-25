# Wisecow DevOps Assessment

A complete, end-to-end DevOps implementation for the **Wisecow** application. This project dockerizes Wisecow, deploys it to a local Kubernetes (Kind) cluster with custom port mappings, secures external traffic via **Nginx Ingress** and **cert-manager (TLS)**, automates CI/CD with **GitHub Actions** and **GHCR** using a self-hosted runner, and includes automated system and application health monitoring scripts.

---

## 🌟 Features & Milestones Completed

1. **Dockerization**: Optimized container build using `ubuntu:22.04` slim runtime, handling CRLF line-ending conversions and installing `fortunes-min` runtime databases.
2. **Kubernetes Deployment**: 2-replica deployment with strict CPU/Memory resource constraints, `tcpSocket` health probes (liveness & readiness), and NodePort service (`30099` mapped to host `4499`).
3. **CI Pipeline (GitHub Actions & GHCR)**: Automated Docker image build and push to GitHub Container Registry (GHCR) on `push` to `main`, tagged with `latest` and `sha-<commit_sha>`.
4. **Python Monitoring Utilities**:
   - `health_monitor.py`: Real-time tracking of CPU, Memory, Disk, and Process count with threshold alerts and rotating file logging.
   - `app_health_checker.py`: HTTP health checker handling Wisecow's single-threaded netcat connection teardown via `Connection: close` headers.
5. **Secure TLS Communication**: Nginx Ingress Controller + cert-manager with a self-signed `ClusterIssuer` terminating HTTPS traffic on `https://localhost`.
6. **Continuous Deployment (CD)**: Self-hosted GitHub Actions runner executing `kubectl set image` updates directly on the local Kind cluster.

---

## 📁 Repository Structure

```text
wisecow/
├── Dockerfile                  # Container build instructions
├── wisecow.sh                  # Wisecow Bash web server source
├── kind-config.yaml            # Kind cluster port mapping (80, 443, 4499)
├── k8s/
│   ├── deployment.yaml         # Kubernetes Deployment (2 replicas, probes, resources)
│   ├── service.yaml            # Kubernetes NodePort Service (Port 4499 -> 30099)
│   └── ingress.yaml            # Nginx Ingress & cert-manager ClusterIssuer (TLS)
├── scripts/
│   ├── health_monitor.py       # System metrics monitor (psutil)
│   ├── app_health_checker.py   # Application HTTP availability checker
│   ├── health_monitor.log      # Log file output (Rotating handler)
│   └── requirements.txt        # Python dependencies (psutil, requests)
├── .github/workflows/
│   └── ci-cd.yaml              # GitHub Actions CI/CD Pipeline
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start & Local Run

### Prerequisites
- [Docker Desktop](https://www.docker.com/)
- [Kind](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Python 3.10+

### 1. Run Wisecow in Docker Locally

```bash
# Build the Docker image
docker build -t wisecow:local .

# Run the container
docker run -d -p 4499:4499 --name wisecow-app wisecow:local

# Verify the app (Returns cowsay ASCII art & fortune quote)
curl.exe http://localhost:4499/

# Stop container
docker rm -f wisecow-app
```

---

## ☸️ Kubernetes Deployment (Kind Cluster)

### 1. Create the Kind Cluster

Use the included `kind-config.yaml` to ensure port 4499 (NodePort) and ports 80/443 (Ingress) are mapped to your host:

```bash
kind create cluster --config kind-config.yaml --name wisecow-cluster
```

### 2. Deploy Application Manifests

```bash
# Load local Docker image into Kind
kind load docker-image wisecow:local --name wisecow-cluster

# Apply Deployment and Service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify Pods and Service
kubectl get pods
kubectl get svc
```

### 3. Verify Direct Access

```bash
curl.exe -m 5 http://localhost:4499/
```

---

## 🔒 TLS & Ingress Setup (HTTPS)

### 1. Install Nginx Ingress Controller & Cert-Manager

```bash
# Install Nginx Ingress Controller for Kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.yaml
```

### 2. Apply Ingress & ClusterIssuer Manifests

```bash
kubectl apply -f k8s/ingress.yaml
```

### 3. Verify HTTPS Access

```bash
# Check certificate status (READY: True)
kubectl get certificate

# Test HTTPS termination (-k for self-signed certificate)
curl.exe -k -m 5 https://localhost/
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow [`.github/workflows/ci-cd.yaml`](file:///.github/workflows/ci-cd.yaml) consists of two jobs:

1. **Build Job (`ubuntu-latest`)**:
   - Logs into **GitHub Container Registry (GHCR)** using `${{ secrets.GITHUB_TOKEN }}`.
   - Builds and tags the Docker image with `latest` and `sha-<commit_sha>`.
   - Pushes the image to `ghcr.io/<owner>/wisecow`.
   - ⚠️ **IMPORTANT GHCR GOTCHA**: Packages pushed to GHCR are **Private** by default, even in public repositories! After your first CI run, you must go to **GitHub → Packages → wisecow → Package settings → Change visibility** and set it to **Public**. Otherwise, anyone pulling your `deployment.yaml` will hit an `ImagePullBackOff` permission error.

2. **Deploy Job (`self-hosted`)**:
   - Runs on the local self-hosted runner connected to your Windows machine.
   - Executes `kubectl set image deployment/wisecow wisecow=ghcr.io/<owner>/wisecow:sha-<commit_sha>`.
   - Performs a rolling update on the local Kind cluster.

---

## 📊 Python Monitoring Scripts

Install dependencies:
```bash
pip install -r scripts/requirements.txt
```

### 1. System Health Monitoring Script
Monitors CPU, Memory, Disk, and Process count. Logs alerts to console and `scripts/health_monitor.log`:

```bash
python scripts/health_monitor.py
```

### 2. Application Health Checker
Checks the HTTP availability of the Wisecow service. Uses `Connection: close` headers to cleanly manage netcat socket teardowns:

```bash
python scripts/app_health_checker.py --url http://localhost:4499 --once
```

---

## 📄 License

This project is open-source under the MIT License.
