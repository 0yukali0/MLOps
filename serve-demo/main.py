import io
import base64
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from ray import serve
from ultralytics import YOLO
from PIL import Image
import numpy as np

fastapi_app = FastAPI()

@serve.deployment
@serve.ingress(fastapi_app)
class FastAPIIngress:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")  # default model

    @fastapi_app.post("/model")
    async def set_model(self, request: Request):
        body = await request.json()
        model_path = body["model_path"]
        self.model = YOLO(model_path)
        return {"message": f"update {model_path}!"}

    @fastapi_app.post("/predict")
    async def predict(self, file: UploadFile = File(...)):
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        results = self.model(image)

        result_img = results[0].plot()

        result_img_rgb = Image.fromarray(result_img[..., ::-1])

        buffered = io.BytesIO()
        result_img_rgb.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        det = results[0].boxes.data.tolist()

        return JSONResponse({
            "detections": det,
            "image_base64": encoded_image
        })


app = FastAPIIngress.bind()
serve.run(app, blocking=True)
