from fastapi import FastAPI, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
async def chat(query: str = Query(..., description="Query")):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}
