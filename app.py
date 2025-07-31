from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging

import os
from dotenv import load_dotenv
from routers import journal, auth, notion, scheduler
from utils.database import init_db, close_db_connection_pool

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    logger.error("exc.errors() %s", exc.errors())
    for error in exc.errors():
        errors.append({
            "field": error["loc"][-1],
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={"errors": errors},
    )

# Include the required routers
if os.getenv("ENV") == "local":
    app.include_router(journal.router, dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])
# app.include_router(auth.router, dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])
app.include_router(notion.router, dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])
app.include_router(scheduler.router, dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])

# Add a ping endpoint
@app.get("/ping", dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])
async def ping():
    return {"message": "pong"}

@app.get("/", dependencies=[Depends(RateLimiter(times=int(os.getenv("RATE_LIMIT_DEFAULT_TIMES", 10)), seconds=int(os.getenv("RATE_LIMIT_DEFAULT_SECONDS", 60))))])
async def root():
    return {"message": "Welcome to my FastAPI app!"}

@app.on_event("startup")
async def startup_event():
    await init_db()
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        redis_client = redis.from_url(redis_url, decode_responses=True)
    else:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0, decode_responses=True)
    await FastAPILimiter.init(redis_client)

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection_pool()
    await FastAPILimiter.close()

# Middleware for 404 rate limiting
@app.middleware("http")
async def not_found_rate_limit_middleware(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        client_ip = request.client.host
        times = int(os.getenv("RATE_LIMIT_404_TIMES", 5))
        seconds = int(os.getenv("RATE_LIMIT_404_SECONDS", 60))
        
        # Manually check rate limit for 404s using a distinct key
        redis_client = FastAPILimiter.redis
        key = f"404_limit:{client_ip}"
        current_count = await redis_client.incr(key)
        if current_count == 1:
            await redis_client.expire(key, seconds)
        
        if current_count > times:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded for 404 routes"},
            )
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found"},
        )
    elif response.status_code == 429: # Handle 429 specifically for general rate limits
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )
    return response

# Custom exception handler for other HTTPExceptions (e.g., 429 from RateLimiter on valid routes)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

