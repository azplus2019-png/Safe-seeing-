from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import shutil
from safe_seeing import SafeSeeing

app = FastAPI(title="Safe Seeing Cloud Pipeline")

# Initialize the engine once
# In a real cloud environment, you might want to load models lazily or use a worker pool
engine = SafeSeeing(model_dir="models")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Simple task status storage
tasks = {}

def process_video_task(task_id: str, input_path: str, output_path: str):
    try:
        tasks[task_id] = "processing"
        engine.run(input_path, output_path)
        tasks[task_id] = "completed"
    except Exception as e:
        print(f"Error processing {task_id}: {e}")
        tasks[task_id] = f"failed: {str(e)}"
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.post("/process")
async def start_processing(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"safe_{file.filename}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    tasks[task_id] = "queued"
    background_tasks.add_task(process_video_task, task_id, input_path, output_path)
    
    return {"task_id": task_id, "status": "queued", "output_filename": f"safe_{file.filename}"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": tasks[task_id]}

@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
