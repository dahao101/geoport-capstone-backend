from PIL import Image
import io
from ultralytics import YOLO
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

# Load models
collision_model = YOLO("backend/services/models/collision/best.pt")
potholes = YOLO("backend/services/models/pothole/best.pt")
cracks = YOLO("backend/services/models/cracks/best.pt")


async def validate_image(image: UploadFile = File()):
    try:
        # Read image file
        image_bytes = await image.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Run YOLO detection for collision
        collision_results = collision_model.predict(image)
        collision_detections = [
            {
                "class": int(box.cls[0]),
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),
            }
            for r in collision_results if hasattr(r, "boxes") and r.boxes
            for box in r.boxes
        ]


        # If collision is detected, return response
        if collision_detections:
            return {
                "status": "success",
                "report_type": "vehicle collision",
                "detections": collision_detections
            }

        # If no collision detections, check for road defects
        defects_results = potholes.predict(image)

        pothole_detections = [
            {
                "class": int(box.cls[0]),
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),
            }
            for r in defects_results if hasattr(r, "boxes") and r.boxes 
            for box in r.boxes
        ]


        if pothole_detections:
            return {
                "status": "success",
                "report_type": "road defects",
                "detections": pothole_detections
            }
        
        
        # If no potholes, check for cracks
        cracks_results = cracks.predict(image)
        cracks_detections = [
            {
                "class": int(box.cls[0]),
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist(),
            }
            for r in cracks_results if hasattr(r, "boxes") and r.boxes 
            for box in r.boxes
        ]

        if cracks_detections:
            return {
                "status": "success",
                "report_type": "road defects",
                "detections": cracks_detections
            }

        # If no detections at all
        return {
                "status": "error",
                "report_type": "Invalid report",
                "message": "No collision or defects detected",
            }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Server error: {str(e)}"})
