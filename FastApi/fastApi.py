from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# uvicorn fastApi:app --reload
# http://127.0.0.1:8000/redoc - detail doc
# http://127.0.0.1:8000/redoc - doc
app = FastAPI()

scheduler = AsyncIOScheduler()

def scheduled_task():
    print("Executing scheduled task")

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

# dependency injection sample
def get_background_tasks(background_tasks: BackgroundTasks):
    return background_tasks

# Database mock
items_db = [{"item_name": "Apple"}, {"item_name": "Mongo"}, {"item_name": "Banana"}]

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI"}

@app.get("/items/", response_model=List[dict])
def read_items(skip: int = 0, limit: int = 10):
    return items_db[skip : skip + limit]

@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int):
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}

# background log writing.
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


def process_data(data: dict):
    # Time-consuming data processing
    time.sleep(5)
    print(f"Processed data: {data}")

def send_email(to: str, subject: str):
    # Simulate email sending
    time.sleep(2)
    print(f"Email sent to {to} with subject '{subject}'")

# multiple background task

@app.post("/process-and-notify/")
async def process_and_notify(
    data: dict, 
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_data, data)
    background_tasks.add_task(send_email, "user@example.com", "Processing complete")
    return {"status": "Processing started"}

# Task management.

task_status: Dict[str, str] = {}

def long_running_task(task_id: str):
    task_status[task_id] = "running"
    # Simulate long task
    time.sleep(10)
    task_status[task_id] = "completed"

@app.post("/start-task/")
async def start_task(background_tasks: BackgroundTasks):
    task_id = "task_123"
    background_tasks.add_task(long_running_task, task_id)
    return {"task_id": task_id, "status": "started"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    return {"task_id": task_id, "status": task_status.get(task_id, "unknown")}

@app.post("/schedule-task/")
async def schedule_task():
    scheduler.add_job(scheduled_task, CronTrigger(hour=0, minute=0))
    return {"message": "Task scheduled to run at 12:00 AM every day"}

# for complex async processing - use celery