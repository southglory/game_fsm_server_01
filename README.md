# FSM 처리 서버 시스템(FastAPI + Redis + Celery + Flower)

해보는거지~

```mermaid
graph TD
  A[클라이언트 요청<br>POST /fsm/transition] --> B[FastAPI 서버]
  B --> C[Celery 태스크 큐 등록]
  C --> D[Celery 워커에서 FSM 처리]
  D --> E[Redis에 상태 저장]
  D --> F[전이 로그 기록 or 후처리]
```

## Step 1: Redis + Celery + Flower 실행

docker-compose up --build

## Step 2: FastAPI는 따로 로컬에서 실행

## 서버 정보

uvicorn main:app --reload

Redis 서버: localhost:6379

Celery 워커: celery-fsm

Flower 대시보드: http://localhost:5555
