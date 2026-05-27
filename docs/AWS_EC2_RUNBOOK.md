# AWS Academy EC2 Runbook

## Prerequisites
- EC2 instance running.
- Security Group allowing inbound HTTP on port 80.
- SSH access configured.
- Git installed.
- Docker installed.
- Docker Compose available.

## Suggested setup
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user
newgrp docker

docker --version
docker compose version
```

If Docker Compose is missing, install the plugin from the package manager available on the image or use the modern Docker Compose plugin package supported by the Amazon Linux version in use.

## Deploy
```bash
git clone <REPO_URL>
cd <PROJECT_FOLDER>
docker compose up --build -d
docker compose ps
```

## Validate on the instance
```bash
curl http://localhost/health/django/
curl http://localhost/health/flask/
curl http://localhost/api/v1/ally-status/
curl http://localhost/api/v1/currency-rate/
```

## Browser checks
- `http://<IP_PUBLICA_EC2>/`
- `http://<IP_PUBLICA_EC2>/games/system-status/`

## Notes
- Nginx is the only public-facing container.
- Django and Flask stay internal to the compose network.
- If PostgreSQL is not activated for the final demo, keep SQLite as documented fallback for stability.
