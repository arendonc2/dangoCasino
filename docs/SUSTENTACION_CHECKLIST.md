# Sustentacion Checklist

## Before presenting
- [ ] AWS EC2 is running.
- [ ] Docker is installed.
- [ ] Docker Compose works.
- [ ] Nginx is responding on port 80.
- [ ] Django health endpoint responds.
- [ ] Flask health endpoint responds.
- [ ] Redis returns PONG.
- [ ] Celery worker is running.
- [ ] English and Spanish switching works.
- [ ] The system status page loads.
- [ ] Key endpoints are reachable.

## Live demo suggestion
1. Open Home.
2. Explain the hybrid architecture.
3. Go to System Status.
4. Show Django health.
5. Show Flask health.
6. Play roulette and show source=flask-roulette.
7. Show Flask logs.
8. Stop Flask.
9. Play again and show source=django-fallback.
10. Show Celery logs.
11. Show /api/v1/player-summary/1/.
12. Show /api/v1/ally-status/.
13. Show /api/v1/currency-rate/.
14. Change language to English.
15. Open README and diagrams.

## Quick commands
```bash
docker compose ps
docker compose logs nginx
docker compose logs django_web
docker compose logs flask_roulette
docker compose logs celery_worker
docker compose exec redis redis-cli ping
docker compose stop flask_roulette
docker compose start flask_roulette
```

## Final validation commands
```bash
docker compose up --build -d
docker compose ps
curl http://localhost/health/django/
curl http://localhost/health/flask/
curl http://localhost/api/v1/ally-status/
curl http://localhost/api/v1/currency-rate/
curl http://localhost/api/v1/player-summary/1/
curl -X POST http://localhost/api/v2/roulette/play \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"bet_type":"number","bet_value":"17","amount":100}'
docker compose exec redis redis-cli ping
docker compose logs celery_worker
```
