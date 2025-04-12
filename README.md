
# CLO835 Project: 2-Tier Web Application Deployment on Amazon EKS

This project involves deploying a two-tier web application using Flask and MySQL on Amazon EKS. The application uses Docker images hosted on AWS ECR and Kubernetes manifests for deployment.

### 📚 **Course Information:**
- **Course:** Portable Technologies in Cloud (**CLO835**)
- **Program:** Cloud Architecture & Administration (**CAA**)
- **Institution:** Seneca Polytechnic

### 👥 **Project Members:**
- [![GitHub](https://img.shields.io/badge/Ranju-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white)](https://github.com/R3NJU)
- [![GitHub](https://img.shields.io/badge/Aisha-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white)](https://github.com/aisha-ansari)
- [![GitHub](https://img.shields.io/badge/Vidhi-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white)](https://github.com/vidhiibisla)

---

## 🚀 **Setup Instructions:**

### Clone the Repository
```bash
git clone -b dev https://github.com/R3NJU/CLO835_Project.git
cd CLO835_Project/
```

### Cloud9 Environment Setup

#### Install `eksctl`
```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/eksctl /usr/local/bin
```

#### Create EKS Cluster
```bash
eksctl create cluster -f eks_config.yaml
```

#### Install `kubectl`
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm -f ./kubectl
```

#### Configure kubeconfig
```bash
aws eks update-kubeconfig --name clo835 --region us-east-1
```

#### Create Namespace
```bash
kubectl create ns final
```

#### Install AWS EBS CSI Driver
```bash
aws eks create-addon --cluster-name clo835 --addon-name aws-ebs-csi-driver --region us-east-1
```

#### Create Image Secret for AWS ECR
```bash
kubectl create secret docker-registry ecr-secret \
--docker-server=638733641367.dkr.ecr.us-east-1.amazonaws.com \
--docker-username=AWS \
--docker-password=$(aws ecr get-login-password --region us-east-1) \
--namespace=final
```

---

## 🛠 **Deploy Application**

Navigate to `k8s_manifests` and apply manifests:
```bash
kubectl apply -f cluster-role.yaml
kubectl apply -f cluster-role-binding.yaml
kubectl apply -f service-account.yaml
kubectl apply -f configmap.yaml
kubectl apply -f mysql-secret.yaml
kubectl apply -f aws-secret.yaml
kubectl apply -f flask-service.yaml
kubectl apply -f mysql-service.yaml
kubectl apply -f pvc.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f flask-deployment.yaml
```

---

## 📋 **Docker Image Management**

### Build & Push Docker Images
```bash
cd webapp
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 638733641367.dkr.ecr.us-east-1.amazonaws.com

docker build -t flask .
docker tag flask:latest 638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:flask
docker push 638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:flask

docker build -t sql -f Dockerfile_mysql .
docker tag sql:latest 638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:sql
docker push 638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:sql
```

### Local Testing
```bash
docker run --name my_db -d -e MYSQL_ROOT_PASSWORD=pw 638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:sql

docker run --name flask_app -d -p 81:8080 \
-e DBHOST=$DBHOST \
-e DBPORT=$DBPORT \
-e DBUSER=$DBUSER \
-e DBPWD=$DBPWD \
-e HEADER_NAME=$HEADER_NAME \
-e IMAGENAME=$IMAGENAME \
-e BUCKET=$BUCKET \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
638733641367.dkr.ecr.us-east-1.amazonaws.com/clo835:flask
```

---

## 📂 **Repository Structure**
```
CLO835_Project/
├── .github/
│   └── workflows/
│       └── ECR_Workflow.yaml
├── k8s_manifests/
│   ├── aws-secret.yaml
│   ├── cluster-role-binding.yaml
│   ├── cluster-role.yaml
│   ├── configmap.yaml
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-secret.yaml
│   ├── mysql-service.yaml
│   ├── pvc.yaml
│   └── service-account.yaml
├── webapp/
│   ├── static/
│   │   └── cover.jpg
│   ├── templates/
│   │   ├── about.html
│   │   ├── addemp.html
│   │   ├── addempoutput.html
│   │   ├── getemp.html
│   │   └── getempoutput.html
│   ├── app.py
│   ├── Dockerfile
│   ├── Dockerfile_mysql
│   ├── mysql.sql
│   └── requirements.txt
├── .gitignore
├── eks_config.yaml
└── README.md
```

---
