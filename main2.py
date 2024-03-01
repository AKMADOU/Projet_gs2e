from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()

def save_file(file, upload_folder):
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), upload_folder: str = "uploads"):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = save_file(file, upload_folder)
    return {"filename": file.filename, "path": file_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
