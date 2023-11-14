from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import asyncio
import os
from fastapi import File
from tempfile import TemporaryDirectory
from api import model

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the API Service"}


@app.post("/predict")
async def predict(file: bytes = File(...)):
    print("predict file:", len(file), type(file))

    # Save the image
    with TemporaryDirectory() as image_dir:
        image_path = os.path.join(image_dir, "test.png")
        with open(image_path, "wb") as output:
            output.write(file)

            # Make prediction
            prediction_results = {}
            prediction_results = model.make_prediction_vertexai(image_path)

    print(prediction_results)
    return prediction_results
