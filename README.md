# Wisecow DevOps Deployment

This repository contains the deployment, containerization, and automation setup for the **Wisecow** application. The goal of this project is to provide a secure, automated, and observable environment for the application to run.

The infrastructure includes a local Kubernetes (Kind) cluster, automated CI/CD via GitHub Actions, TLS-secured ingress, system monitoring scripts, and a strict Zero-Trust security posture enforced by KubeArmor.

---

## Features & Implementation

1. **Containerization**: The app is containerized using `ubuntu:22.04`. The Dockerfile installs necessary runtime dependencies (`fortune`, `cowsay`, `netcat`) and handles Windows-to-Linux line ending conversions.
2. **Kubernetes Architecture**: Deployed with 2 replicas, strict resource limits, and readiness/liveness health probes. External access is routed through a NodePort service.
3. **GitOps CI/CD**: GitHub Actions automates building and pushing Docker images to GHCR, and updates the Kustomize manifests. **ArgoCD** runs inside the cluster to automatically pull and synchronize the changes, enforcing a true GitOps pull-based deployment model.
4. **Monitoring**: Custom Python scripts track system health (CPU, Memory, Disk) and application availability, logging alerts when thresholds are breached.
5. **TLS Encryption**: Ingress-Nginx and cert-manager terminate HTTPS traffic securely using a local ClusterIssuer.
6. **Zero-Trust Security**: KubeArmor policies restrict what the container is actually allowed to do at the kernel level, mitigating potential compromises.

---

## 📁 Repository Structure

```text
wisecow/
├── Dockerfile                  # Container build instructions
├── wisecow.sh                  # Application source code
├── kind-config.yaml            # Kind cluster configuration and port mappings
├── argocd/
│   └── application.yaml        # ArgoCD Application definition
├── k8s/
│   ├── deployment.yaml         # App deployment, probes, and resource limits
│   ├── service.yaml            # NodePort service configuration
│   ├── ingress.yaml            # Ingress routing and TLS configuration
│   └── kustomization.yaml      # Kustomize manifest for GitOps image updates
├── kubearmor/
│   ├── policy.yaml             # KubeArmor security policy
│   └── violation_screenshot.png # Evidence of policy enforcement
├── scripts/
│   ├── health_monitor.py       # System resource monitoring script
│   ├── app_health_checker.py   # Application endpoint health checker
│   └── requirements.txt        # Python dependencies
└── .github/workflows/
    └── ci-cd.yaml              # GitHub Actions pipeline
```

---

## 🛡️ Zero-Trust Security with KubeArmor

By default, if an attacker gains access to a container, they can explore the file system, execute arbitrary binaries, and attempt to escalate privileges. 

To prevent this, we implemented a **Zero-Trust KubeArmor Policy** (`kubearmor/policy.yaml`). Instead of trying to guess what a hacker might do, this policy explicitly defines the *only* things the Wisecow application is allowed to do. Everything else is blocked or flagged.

**What the policy actually does:**
* **Process Execution**: Wisecow only needs a few tools to run (`bash`, `sh`, `nc`, `fortune`, `cowsay`, `cat`). The policy allows these and audits attempts to run anything else (like `curl`, `python`, or `nmap`).
* **File System Protection**: It explicitly blocks access to sensitive system files that the app never needs to read, such as `/etc/shadow` (password hashes) and `/etc/passwd`.
* **Network Restrictions**: It allows TCP connections (required for the web server) but explicitly blocks UDP and RAW sockets, preventing attackers from establishing reverse shells or scanning networks.
* **Capabilities**: It prevents the container processes from acquiring elevated Linux capabilities like `net_admin` or `sys_admin`.

### How to apply and test the policy:

```bash
# 1. Install KubeArmor via Helm
helm repo add kubearmor https://kubearmor.github.io/charts
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace

# 2. Apply the security policy
kubectl apply -f kubearmor/policy.yaml

# 3. Test the policy by attempting an unauthorized action
kubectl exec deploy/wisecow -- cat /etc/shadow
```
*(Note: On local Kind/WSL2 environments, KubeArmor operates in Audit Mode. Unauthorized actions are logged to the KubeArmor telemetry stream rather than hard-blocked.)*

---

## 🚀 Running the Project

### Prerequisites
- Docker & Kind
- kubectl & Helm
- Python 3.10+

### 1. Cluster Setup & Deployment

```bash
# Create the local cluster with custom port mappings
kind create cluster --config kind-config.yaml --name wisecow-cluster

# Build and load the image
docker build -t wisecow:local .
kind load docker-image wisecow:local --name wisecow-cluster

# Deploy the application
kubectl apply -f k8s/
```

### 2. TLS & Ingress Setup

```bash
# Install Ingress-Nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.yaml

# Apply local Ingress configuration
kubectl apply -f k8s/ingress.yaml
```

### 3. Verify Access

```bash
# Standard HTTP
curl.exe -m 5 http://localhost:4499/

# Secure HTTPS
curl.exe -k -m 5 https://localhost/
```

---

## 🔄 GitOps CI/CD with ArgoCD

The continuous deployment pipeline follows a modern **GitOps** architecture:
1. **GitHub Actions** builds the Docker image and pushes it to GitHub Container Registry (GHCR).
2. The pipeline then uses **Kustomize** to update the image tag in `k8s/kustomization.yaml` and automatically commits this change back to the repository.
3. **ArgoCD**, running natively inside the Kubernetes cluster, detects the new commit and automatically synchronizes the live cluster state to match the repository.

> **Important Note regarding GHCR**: Packages pushed to GHCR are Private by default, even if the repository is public. If you fork this project, you must manually navigate to **Package Settings** in GitHub and change the image visibility to **Public** to avoid `ImagePullBackOff` errors in Kubernetes.

---

## 📊 Monitoring Scripts

The `scripts/` directory contains tools to observe system and application health.

```bash
pip install -r scripts/requirements.txt

# Monitor System Resources (CPU, Memory, Disk)
python scripts/health_monitor.py

# Check Application Uptime
python scripts/app_health_checker.py --url http://localhost:4499 --once
```
