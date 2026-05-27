# Container Diagram

```mermaid
flowchart LR
    U[Usuario] --> N[Nginx API Gateway]
    N --> D[Django Web]
    N --> F[Flask Roulette Service]
    D --> R[(Redis)]
    R --> C[Celery Worker]
    D --> DB[(SQLite / PostgreSQL fallback)]
    D --> A[Ally Service]
    D --> X[External Currency API]
    F --> D
    C --> D
```

## Notes
- Nginx is the only public entry point.
- Django keeps the UI and orchestration.
- Flask executes the main roulette flow.
- Redis and Celery handle asynchronous audit tasks.
- Database stays SQLite for final demo stability; PostgreSQL is documented as a future improvement.
