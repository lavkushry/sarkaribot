# 🚀 SarkariBot Deployment Guide

## Overview

This comprehensive guide covers deploying SarkariBot in various environments, from development to production. The system supports multiple deployment strategies including Docker, cloud platforms, and traditional server deployments.

## 📋 Prerequisites

### System Requirements

#### Minimum (Development)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+, CentOS 8+, or Docker

#### Recommended (Production)
- **CPU**: 4-8 cores
- **RAM**: 16-32GB
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 22.04 LTS
- **Load Balancer**: Nginx/HAProxy
- **Database**: PostgreSQL 14+
- **Cache**: Redis 6+

### Software Dependencies
```bash
# Core requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ / MySQL 8+
- Redis 6+
- Nginx 1.20+

# Optional but recommended
- Docker 24+
- Docker Compose 2.0+
- SSL Certificate (Let's Encrypt)
- CDN (CloudFlare)
```

## 🐳 Docker Deployment (Recommended)

### Production Docker Setup

1. **Clone and prepare the repository**:
```bash
git clone https://github.com/yourusername/sarkaribot.git
cd sarkaribot
cp .env.example .env
```

2. **Configure environment variables**:
```bash
# Edit .env file with production values
nano .env
```

```env
# Database Configuration
POSTGRES_DB=sarkaribot_prod
POSTGRES_USER=sarkaribot_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=your_super_secret_key_here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# AWS S3 Configuration (for media files)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=sarkaribot-media
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
ENABLE_MONITORING=True

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

3. **Create production docker-compose.yml**:
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - sarkaribot_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - sarkaribot_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./backend/logs:/app/logs
      - media_volume:/app/media
      - static_volume:/app/static
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - sarkaribot_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 5

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    command: celery -A config worker -l info --concurrency=4
    env_file: .env
    volumes:
      - ./backend/logs:/app/logs
    depends_on:
      - db
      - redis
      - backend
    networks:
      - sarkaribot_network
    healthcheck:
      test: ["CMD", "celery", "-A", "config", "inspect", "ping"]
      interval: 60s
      timeout: 10s
      retries: 5

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    volumes:
      - ./backend/logs:/app/logs
    depends_on:
      - db
      - redis
      - backend
    networks:
      - sarkaribot_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        REACT_APP_API_URL: https://yourdomain.com/api
        REACT_APP_WS_URL: wss://yourdomain.com/ws
    restart: unless-stopped
    volumes:
      - frontend_build:/app/build
    networks:
      - sarkaribot_network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - frontend_build:/var/www/html
    depends_on:
      - backend
      - frontend
    networks:
      - sarkaribot_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  certbot:
    image: certbot/certbot
    restart: unless-stopped
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: certonly --webroot -w /var/www/certbot --force-renewal --email your-email@domain.com -d yourdomain.com -d www.yourdomain.com --agree-tos

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  frontend_build:

networks:
  sarkaribot_network:
    driver: bridge
```

4. **Create production Dockerfiles**:

Backend Dockerfile.prod:
```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        libpng-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Change ownership to django user
RUN chown -R django:django /app

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/static \
    && chown -R django:django /app/logs /app/media /app/static

# Switch to django user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "50", "--preload", "--timeout", "30", "--keep-alive", "2", "config.wsgi:application"]
```

Frontend Dockerfile.prod:
```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build arguments
ARG REACT_APP_API_URL
ARG REACT_APP_WS_URL

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

5. **Deploy the application**:
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Load initial data
docker-compose -f docker-compose.prod.yml exec backend python manage.py loaddata fixtures/initial_data.json
```

### SSL Certificate Setup

1. **Initial certificate generation**:
```bash
# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Generate certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --standalone --email your-email@domain.com -d yourdomain.com -d www.yourdomain.com

# Start nginx
docker-compose -f docker-compose.prod.yml start nginx
```

2. **Auto-renewal setup**:
```bash
# Add to crontab
echo "0 12 * * * /usr/local/bin/docker-compose -f /path/to/sarkaribot/docker-compose.prod.yml exec certbot renew --quiet" | crontab -
```

## 🌐 Cloud Platform Deployments

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create task definitions**:
```json
{
  "family": "sarkaribot-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/sarkaribot-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.production"
        }
      ],
      "secrets": [
        {
          "name": "DJANGO_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:sarkaribot/django-secret"
        },
        {
          "name": "POSTGRES_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:sarkaribot/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/sarkaribot-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health/ || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

2. **Create RDS instance**:
```bash
aws rds create-db-instance \
    --db-instance-identifier sarkaribot-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.3 \
    --allocated-storage 100 \
    --storage-type gp2 \
    --db-name sarkaribot \
    --master-username postgres \
    --master-user-password YourSecurePassword \
    --vpc-security-group-ids sg-xxxxxxxx \
    --db-subnet-group-name sarkaribot-db-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted
```

3. **Create ElastiCache Redis cluster**:
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id sarkaribot-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1 \
    --cache-parameter-group-name default.redis7 \
    --cache-subnet-group-name sarkaribot-cache-subnet-group \
    --security-group-ids sg-xxxxxxxx
```

4. **Deploy with CloudFormation**:
```yaml
# cloudformation-template.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'SarkariBot Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
  
  DomainName:
    Type: String
    Description: Domain name for the application
    Default: sarkaribot.com

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "${Environment}-sarkaribot-vpc"

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${Environment}-sarkaribot-alb"
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${Environment}-sarkaribot-cluster"
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT

  # RDS Database
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub "${Environment}-sarkaribot-db"
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: '15.3'
      AllocatedStorage: 100
      StorageType: gp2
      DBName: sarkaribot
      MasterUsername: postgres
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      MultiAZ: true
      StorageEncrypted: true

Outputs:
  LoadBalancerDNS:
    Description: DNS name of the load balancer
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub "${Environment}-sarkaribot-alb-dns"
```

### Digital Ocean Deployment

1. **Create Kubernetes cluster**:
```bash
doctl kubernetes cluster create sarkaribot-cluster \
    --region nyc1 \
    --version 1.27.4-do.0 \
    --count 3 \
    --size s-2vcpu-2gb
```

2. **Deploy with Kubernetes manifests**:
```yaml
# k8s/namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: sarkaribot

---
# k8s/configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sarkaribot-config
  namespace: sarkaribot
data:
  DJANGO_SETTINGS_MODULE: "config.settings.production"
  POSTGRES_HOST: "postgres-service"
  REDIS_URL: "redis://redis-service:6379/0"

---
# k8s/secret.yml
apiVersion: v1
kind: Secret
metadata:
  name: sarkaribot-secrets
  namespace: sarkaribot
type: Opaque
data:
  DJANGO_SECRET_KEY: <base64-encoded-secret>
  POSTGRES_PASSWORD: <base64-encoded-password>

---
# k8s/backend-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: sarkaribot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/sarkaribot-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: sarkaribot-config
        - secretRef:
            name: sarkaribot-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
# k8s/backend-service.yml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: sarkaribot
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

## 🖥️ Traditional Server Deployment

### Ubuntu Server Setup

1. **System preparation**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

2. **Database setup**:
```bash
# Configure PostgreSQL
sudo -u postgres psql

CREATE DATABASE sarkaribot_prod;
CREATE USER sarkaribot_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sarkaribot_prod TO sarkaribot_user;
ALTER USER sarkaribot_user CREATEDB;
\q

# Configure Redis
sudo nano /etc/redis/redis.conf
# Uncomment and set: maxmemory 2gb
# Uncomment and set: maxmemory-policy allkeys-lru

sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

3. **Application deployment**:
```bash
# Create application user
sudo adduser --system --group --home /opt/sarkaribot sarkaribot

# Clone repository
sudo -u sarkaribot git clone https://github.com/yourusername/sarkaribot.git /opt/sarkaribot/app
cd /opt/sarkaribot/app

# Setup Python environment
sudo -u sarkaribot python3.11 -m venv /opt/sarkaribot/venv
sudo -u sarkaribot /opt/sarkaribot/venv/bin/pip install -r backend/requirements/production.txt

# Setup environment variables
sudo -u sarkaribot cp .env.example .env
sudo -u sarkaribot nano .env

# Run migrations
sudo -u sarkaribot /opt/sarkaribot/venv/bin/python backend/manage.py migrate
sudo -u sarkaribot /opt/sarkaribot/venv/bin/python backend/manage.py collectstatic --noinput
sudo -u sarkaribot /opt/sarkaribot/venv/bin/python backend/manage.py createsuperuser
```

4. **Frontend build**:
```bash
cd /opt/sarkaribot/app/frontend
sudo -u sarkaribot npm install
sudo -u sarkaribot npm run build
```

5. **Configure Supervisor**:
```ini
# /etc/supervisor/conf.d/sarkaribot.conf
[program:sarkaribot-backend]
command=/opt/sarkaribot/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --worker-class gevent config.wsgi:application
directory=/opt/sarkaribot/app/backend
user=sarkaribot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/sarkaribot/backend.log

[program:sarkaribot-celery]
command=/opt/sarkaribot/venv/bin/celery -A config worker -l info --concurrency=4
directory=/opt/sarkaribot/app/backend
user=sarkaribot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/sarkaribot/celery.log

[program:sarkaribot-celery-beat]
command=/opt/sarkaribot/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/opt/sarkaribot/app/backend
user=sarkaribot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/sarkaribot/celery-beat.log
```

6. **Configure Nginx**:
```nginx
# /etc/nginx/sites-available/sarkaribot
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    root /opt/sarkaribot/app/frontend/build;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types application/javascript application/json text/css text/javascript text/xml application/xml application/xml+rss;

    # Cache static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
    }

    # Admin interface
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/sarkaribot/app/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/sarkaribot/app/backend/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React app
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## 📊 Monitoring and Logging

### Production Monitoring Setup

1. **Install monitoring tools**:
```bash
# Install Prometheus
docker run -d --name prometheus \
    -p 9090:9090 \
    -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus

# Install Grafana
docker run -d --name grafana \
    -p 3000:3000 \
    -v grafana-storage:/var/lib/grafana \
    grafana/grafana
```

2. **Configure Prometheus**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sarkaribot-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

3. **Setup centralized logging**:
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logs:/var/log/sarkaribot
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
```

## 🔄 Backup and Recovery

### Database Backup

1. **Automated backup script**:
```bash
#!/bin/bash
# /opt/sarkaribot/scripts/backup.sh

BACKUP_DIR="/opt/sarkaribot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sarkaribot_prod"
DB_USER="sarkaribot_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/sarkaribot/app/backend/media/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://sarkaribot-backups/
aws s3 cp $BACKUP_DIR/media_backup_$DATE.tar.gz s3://sarkaribot-backups/

echo "Backup completed: $DATE"
```

2. **Setup cron job**:
```bash
# Add to crontab
0 2 * * * /opt/sarkaribot/scripts/backup.sh >> /var/log/sarkaribot/backup.log 2>&1
```

### Disaster Recovery

1. **Recovery script**:
```bash
#!/bin/bash
# /opt/sarkaribot/scripts/restore.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
sudo supervisorctl stop sarkaribot-backend sarkaribot-celery sarkaribot-celery-beat

# Restore database
gunzip -c $BACKUP_FILE | psql -h localhost -U sarkaribot_user -d sarkaribot_prod

# Restart services
sudo supervisorctl start sarkaribot-backend sarkaribot-celery sarkaribot-celery-beat

echo "Recovery completed"
```

## 🚀 Performance Optimization

### Database Optimization

1. **PostgreSQL configuration**:
```conf
# /etc/postgresql/15/main/postgresql.conf

# Memory settings
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 256MB
maintenance_work_mem = 1GB

# Connection settings
max_connections = 200
max_worker_processes = 8
max_parallel_workers = 8
max_parallel_workers_per_gather = 4

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 64MB
default_statistics_target = 100

# Query optimization
random_page_cost = 1.1
effective_io_concurrency = 200
```

2. **Redis optimization**:
```conf
# /etc/redis/redis.conf

maxmemory 8gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-keepalive 300
timeout 0
```

### CDN Setup

1. **CloudFlare configuration**:
```javascript
// CloudFlare Workers script
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Cache static assets aggressively
  if (url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$/)) {
    const response = await fetch(request)
    const newResponse = new Response(response.body, response)
    newResponse.headers.set('Cache-Control', 'public, max-age=31536000')
    return newResponse
  }
  
  // Cache API responses for 5 minutes
  if (url.pathname.startsWith('/api/')) {
    const cacheKey = new Request(url.toString(), request)
    const cache = caches.default
    
    let response = await cache.match(cacheKey)
    
    if (!response) {
      response = await fetch(request)
      const newResponse = new Response(response.body, response)
      newResponse.headers.set('Cache-Control', 'public, max-age=300')
      cache.put(cacheKey, newResponse.clone())
      return newResponse
    }
    
    return response
  }
  
  return fetch(request)
}
```

## 🔒 Security Hardening

### Server Security

1. **Firewall configuration**:
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Fail2ban configuration
sudo apt install fail2ban
sudo nano /etc/fail2ban/jail.local
```

2. **SSL/TLS hardening**:
```nginx
# /etc/nginx/conf.d/ssl.conf
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

add_header Strict-Transport-Security "max-age=63072000" always;
```

### Application Security

1. **Django security settings**:
```python
# config/settings/production.py

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_REFERRER_POLICY = "same-origin"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Static files collected
- [ ] SSL certificates obtained
- [ ] DNS records configured
- [ ] Monitoring setup completed
- [ ] Backup procedures tested
- [ ] Security hardening applied

### Deployment
- [ ] Code deployed to production
- [ ] Database migrations applied
- [ ] Static files served correctly
- [ ] SSL/HTTPS working
- [ ] All services started
- [ ] Health checks passing
- [ ] Monitoring active
- [ ] Log aggregation working

### Post-Deployment
- [ ] Functionality testing completed
- [ ] Performance metrics within bounds
- [ ] Error tracking active
- [ ] Backup procedures verified
- [ ] Documentation updated
- [ ] Team notified of deployment

## 🚨 Troubleshooting

### Common Issues

1. **Database connection errors**:
```bash
# Check database status
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT 1;"

# Check Django database connection
python manage.py dbshell
```

2. **Static files not loading**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

3. **Celery not processing tasks**:
```bash
# Check Celery status
celery -A config inspect ping
celery -A config inspect active

# Check Redis connection
redis-cli ping
```

4. **High memory usage**:
```bash
# Monitor memory usage
htop
free -h

# Check for memory leaks
ps aux --sort=-%mem | head
```

## 📞 Support

For deployment support:
- **Documentation**: [Deployment Guide](https://docs.sarkaribot.com/deployment/)
- **Support Email**: devops@sarkaribot.com
- **Discord**: [#deployment channel](https://discord.gg/sarkaribot)
- **Emergency**: +1-XXX-XXX-XXXX (24/7 support)

---

**Deployment Guide Version**: 1.0  
**Last Updated**: August 1, 2024  
**Supported Platforms**: Docker, AWS, DigitalOcean, Ubuntu 20.04+
