












import os
import io
import re
import uuid
import shutil
import fitz  # PyMuPDF
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
from google.cloud import vision
from dotenv import load_dotenv

# ===============================
# 🔹 Environment Setup
# ===============================
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
load_dotenv()

GOOGLE_CREDS_PATH = (
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    or r"D:\Identity_verification\google-cloud-credentials.json"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDS_PATH

# ===============================
# 🔹 FastAPI Setup
# ===============================
app = FastAPI(title="Identity Verification API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 🔹 Create Upload Directories
# ===============================
UPLOAD_DIR = "uploads"
for folder in ["aadhaar", "selfie", "imei"]:
    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)

# Google Vision client
client = vision.ImageAnnotatorClient()


# ===============================
# 🔹 File Conversion Helpers
# ===============================
def ensure_supported_format(file_path):
    """
    Convert PDF/AVIF → JPG.
    Always return the usable JPG image path.
    """
    ext = file_path.lower()

    # ----- AVIF → JPG -----
    if ext.endswith(".avif"):
        img = Image.open(file_path).convert("RGB")
        new_path = file_path.replace(".avif", ".jpg")
        img.save(new_path, "JPEG")
        return new_path

    # ----- PDF → JPG -----
    if ext.endswith(".pdf"):
        pdf_doc = fitz.open(file_path)
        page = pdf_doc.load_page(0)
        pix = page.get_pixmap()
        new_path = file_path.replace(".pdf", ".jpg")
        pix.save(new_path)
        pdf_doc.close()
        return new_path

    return file_path







# ===============================
# 🔹 Face Verification Logic
# ===============================
def verify_faces(aadhaar_path, selfie_path):
    try:
        aadhaar_img = ensure_supported_format(aadhaar_path)
        selfie_img = ensure_supported_format(selfie_path)

        result = DeepFace.verify(
            img1_path=aadhaar_img,
            img2_path=selfie_img,
            model_name="ArcFace",
            detector_backend="retinaface",
            distance_metric="cosine",
            enforce_detection=False,
        )

        similarity = round(1 - result["distance"], 4)
        verified = similarity >= 0.45  # threshold

        return {
            "face_match": verified,
            "similarity_score": similarity,
            "model_used": result.get("model", "ArcFace"),
        }

    except Exception as e:
        return {
            "face_match": False,
            "similarity_score": 0.0,
            "error": str(e),
        }





# ===============================
# 🔹 Main API Endpoint
# ===============================
@app.post("/verify")
async def verify_identity(
    aadhaar: UploadFile = File(...),
    selfie: UploadFile = File(...),
    
):
    try:
        # ----- Save files -----
        aadhaar_path = os.path.join(UPLOAD_DIR, "aadhaar", f"{uuid.uuid4()}_{aadhaar.filename}")
        selfie_path = os.path.join(UPLOAD_DIR, "selfie", f"{uuid.uuid4()}_{selfie.filename}")
        

        for uploaded, path in [(aadhaar, aadhaar_path), (selfie, selfie_path) ]:
            with open(path, "wb") as f:
                shutil.copyfileobj(uploaded.file, f)

        # ----- Face Verification -----
        face_result = verify_faces(aadhaar_path, selfie_path)

        
        # Aadhaar validation
        aadhaar_valid = "aadhaar" in aadhaar_text

       
       
        # ----- Final status -----
        final_status = aadhaar_valid and face_result["face_match"]

        # ----- Response -----
        return JSONResponse(
            {
                "verification_status": bool(final_status),
                "face_match": face_result["face_match"],
                "similarity_score": face_result["similarity_score"],
                "model_used": face_result["model_used"],
                "aadhaar_valid": aadhaar_valid,
                "files_saved": {
                    "aadhaar": aadhaar_path,
                    "selfie": selfie_path,
                   
                },
            }
        )

    except Exception as e:
        return JSONResponse({"verification_status": False, "error": str(e)}, status_code=500)


# ===============================
# 🔹 Run Server
# ===============================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)

































