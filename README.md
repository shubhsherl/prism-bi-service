# prism-service

1. Add env variables to .env file
```
API_KEY=xxxxxxxxxxxxxx-xxxxx-xxxxx
CRUX_API_KEY=xxxxxxxxxxxxxx-xxxxx-xxxxx
CX_ID=xxxxxxxxxxxxxx
REDIS_PASSWORD=xxxxxxxxxxx
WPT_URL=http://52.204.137.156:8000
WPT_API_KEY=xxxxxxxxxxxxxx-xxxxx-xxxxx
```

2. Run and up docker compose

```
docker-compose up -d # to run in background
<OR>
docker-compose up # to run in foreground
```

### Stop docker compose
```
docker-compose down
```