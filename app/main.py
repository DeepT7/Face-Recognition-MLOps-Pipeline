import cv2 
import sys 
import os
import numpy as np
import json
import onnxruntime as ort
import logging 
import threading
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import RedirectResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from supabase import create_client
import tritonclient.http as httpclient
import  tritonclient.grpc as grpcclient
load_dotenv()
from app.core.config import FINAL_SETUP_DIR, GALLERY_DIR, VERIFICATION_THRESHOLD

sys.path.append("./edgeface")
from app.utils import extract_embedding, extract_embedding_from_triton, load_gallery_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# API Key Configuration
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

API_KEYS = {ADMIN_API_KEY: "admin"} if ADMIN_API_KEY else {}

# Create an API key header instance
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True, description="Admin API key for authentication")

# Create a Supabase client instance
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scalable Face Matching Gateway",
    description = "An API for face verification, registration, and management.",
    version = "1.1.0"
)

# Mount static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
# Initialize Triton client (if needed for future GPU inference)
triton_client = None
TRITON_MODEL_NAME = "face_matching_model"
try:
    triton_grpc_url = os.getenv("TRITON_SERVER_URL", "localhost:8001")
    triton_client = grpcclient.InferenceServerClient(url=triton_grpc_url, verbose=False)
    logger.info(f"Triton gRPC client initialized at {triton_grpc_url}")
except Exception as e:
    logger.error(f"Error initializing Triton gRPC client: {e}")

# A lock to make sure we don't have race conditions when updating the gallery
gallery_lock = threading.Lock()
# --- Model and Data Loading ---

# MLOps Tip: Load model into RAM at startup to reduce latency
session = ort.InferenceSession("checkpoints/edgeface_base.onnx", providers=['CPUExecutionProvider'])
input_name = session.get_inputs()[0].name
logger.info(f"ONNX model loaded. Input name: {input_name}")

# Load initial gallery data
gallery_data, gallery_ids, gallery_embeddings = load_gallery_data(supabase_client)
# logger.info(f"Debug: Gallery data keys: {list(gallery_data.keys())}")
# logger.info(f"Debug: Gallery IDs: {gallery_ids}")

# --- API Endpoints ---
async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    "Verify the provided API key against the allowed keys. Raises 401 if invalid."
    if api_key not in API_KEYS:
        logger.warning(f"Unauthorized access attempt with API key: {api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[api_key]

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to the API documentation."""
    return RedirectResponse(url="/docs")

@app.get("/web", include_in_schema=False)
async def web_interface():
    """Serve the web interface for the face matching gateway."""
    return FileResponse(f"{base_dir}/templates/index.html", media_type="text/html")

@app.get("/test", include_in_schema=False)
async def test_ui():
    """Serve the test UI for authentication testing."""
    test_ui_path = os.path.join(os.path.dirname(__file__), "test_ui.html")
    return FileResponse(test_ui_path, media_type="text/html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Satisfy browser favicon requests to prevent 404 logs."""
    return Response(status_code=204)

@app.post("/verify")
async def verify(file: UploadFile = File(...), person_id: str = Query(..., description="The ID of the person to verify against")):
    person_id = f"{int(person_id):06d}"
    logger.debug(f"Debug: Verifying person_id: {person_id}, in gallery: {person_id in gallery_data}")
    image_bytes = await file.read()
    # probe_embedding = extract_embedding(image_bytes)
    probe_embedding = extract_embedding_from_triton(image_bytes, triton_client=triton_client, model_name=TRITON_MODEL_NAME)

    if probe_embedding is None:
        raise HTTPException(status_code=400, detail="Could not detect a face in the uploaded image")

    with gallery_lock:
        if person_id not in gallery_data:
            raise HTTPException(status_code=404, detail=f"Person ID '{person_id}' not found in database.")

        target_gallery_embedding = gallery_data[person_id]['embedding']
        person_name = gallery_data[person_id]['name']
        
        similarity = np.dot(target_gallery_embedding, probe_embedding)

        return {
            "id": person_id,
            "name": person_name,
            "similarity": float(similarity),
            "status": "Successfully verified" if similarity > VERIFICATION_THRESHOLD else "Failed to verify"
        }

@app.get("/users")
async def get_all_users(client_type: str = Depends(verify_api_key)):
    """
    Retrieves all users from the gallery.
    """
    try:
        # Supabase has a default limit of 1000 rows, so we need to paginate
        all_users = []
        page_size = 1000
        offset = 0

        while True:
            response = supabase_client.table("face_users").select("id, name, gallery_path").range(offset, offset + page_size - 1).execute()
            users = response.data

            if not users:
                break

            all_users.extend(users)
            offset += page_size

            # Safety check to prevent infinite loops
            if len(users) < page_size:
                break

        return {"status": "success", "users": all_users, "count": len(all_users)}
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@app.post("/register", status_code=201)
async def register(person_name: str = Query(..., description="Name of the new person"), 
                   file: UploadFile = File(...),
                   client_type: str = Depends(verify_api_key)):
    """
    Registers a new person by adding their face to the gallery.
    Requires valid API Key in X-API-Key header.
    """
    logger.info(f"Registration request from {client_type}")
    image_bytes = await file.read()
    # new_embedding = extract_embedding(image_bytes)
    new_embedding = extract_embedding_from_triton(image_bytes, triton_client=triton_client, model_name=TRITON_MODEL_NAME)
    if new_embedding is None:
        raise HTTPException(status_code=400, detail="Could not detect a face in the uploaded image. Registration failed.")

    with gallery_lock:
        # Use global variables
        global gallery_data, gallery_ids, gallery_embeddings

        try:
            # 1. Query Supabase to get the max ID
            response = supabase_client.table("face_users").select("id").order("id", desc=True).limit(1).execute()
            users = response.data
            if users:
                max_id = int(users[0]['id'])
                new_id = max_id + 1
            else:
                new_id = 1
            
            person_id = f"{new_id:06d}"

            # 2. Prepare image filename and upload to Supabase storage
            safe_person_name = "".join(c for c in person_name.strip().replace(" ", "_") if c.isalnum() or c == "_")
            image_filename = f"{safe_person_name}_{person_id}.jpg"
            storage_path = f"gallery/{image_filename}"
            
            # Upload image to Supabase bucket 'face_users'
            try:
                supabase_client.storage.from_("face_users").upload(storage_path, image_bytes)
                logger.info(f"Successfully uploaded image to Supabase: {storage_path}")
            except Exception as e:
                logger.error(f"Error uploading image to Supabase: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

            # 3. Prepare data for Supabase
            embedding_list = new_embedding.tolist()
            data = {
                "id": person_id,
                "name": person_name,
                "embedding": embedding_list,
                "gallery_path": storage_path
            }
            supabase_client.table("face_users").upsert(data).execute()

            # 4 Save image to local gallery directory for backup (optional)
            local_image_path = os.path.join(GALLERY_DIR, image_filename)
            try:
                with open(local_image_path, "wb") as f:
                    f.write(image_bytes)
                logger.info(f"Successfully saved image to local gallery: {local_image_path}")
            except Exception as e:
                logger.warning(f"Could not save image to local gallery: {e}")

            # 5. Update in-memory gallery
            gallery_data[person_id] = {'name': person_name, 'embedding': new_embedding}
            gallery_ids.append(person_id)
            if gallery_embeddings.size == 0:
                gallery_embeddings = np.expand_dims(new_embedding, axis=0)
            else:
                gallery_embeddings = np.vstack([gallery_embeddings, new_embedding])

            logger.info(f"Successfully registered new person: ID={person_id}, Name={person_name}")
            return {"status": "success", "person_id": person_id, "person_name": person_name}
        
        except Exception as e:
            logger.error(f"Error registering new person {person_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.delete("/person/{person_id}")
async def delete_person(person_id: str,
                        client_type: str = Depends(verify_api_key)):
    """
    Deletes a person from the gallery.
    """
    person_id = f"{int(person_id):06d}"
    logger.info(f"Deletion request for person_id: {person_id} from {client_type}")
    with gallery_lock:
        global gallery_data, gallery_ids, gallery_embeddings
        logger.info(f"Debug: Deleting person_id: {person_id}, in gallery: {person_id in gallery_data}")
        # 1. Check if the person exists in memory
        if person_id not in gallery_data:
            raise HTTPException(status_code=404, detail=f"Person with ID '{person_id}' not found.")

        try:
            # 2. Get gallery_path before deleting (for image file deletion)
            try:
                response = supabase_client.table("face_users").select("gallery_path").eq("id", person_id).execute()
                gallery_path = response.data[0]['gallery_path'] if response.data else None
            except Exception as e:
                gallery_path = None
                logger.warning(f"Could not retrieve gallery_path before deletion: {e}")
            
            # 3. Delete from Supabase
            supabase_client.table("face_users").delete().eq("id", person_id).execute()
            
            # 4. Delete from Supabase storage
            if gallery_path:
                try: 
                    supabase_client.storage.from_("face_users").remove([gallery_path])
                    logger.info(f"Successfully deleted image from Supabase storage: {gallery_path}")
                except Exception as e:
                    logger.warning(f"Could not delete image from Supabase storage: {e}")

            # 5. Delete image from disk
            if gallery_path:
                try:
                    image_path_full = os.path.join(FINAL_SETUP_DIR, gallery_path)
                    if os.path.exists(image_path_full):
                        os.remove(image_path_full)
                except Exception as e:
                    logger.warning(f"Could not delete image file: {e}")
            
            # 6. Update in-memory data
            idx_to_remove = gallery_ids.index(person_id)
            del gallery_data[person_id]
            gallery_ids.pop(idx_to_remove)
            gallery_embeddings = np.delete(gallery_embeddings, idx_to_remove, axis=0)

            logger.info(f"Successfully deleted person: ID={person_id}")
            return {"status": "success", "message": f"Person with ID '{person_id}' has been deleted."}
        
        except Exception as e:
            logger.error(f"Error deleting person {person_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@app.get("/debug/gallery")
async def debug_gallery():
    """
    Debug endpoint to view the current gallery data.
    """
    logger.info("Debug: Viewing gallery data.")
    return {
        "gallery_data_keys": list(gallery_data.keys()),
        "gallery_ids": gallery_ids,
        "count": len(gallery_ids)
    }

@app.get("/health")
async def health_check():
    triton_health = {
        "configured_url": triton_grpc_url,
        "client_initialized": triton_client is not None,
        "server_ready": False,
        "model_name": TRITON_MODEL_NAME,
        "model_ready": False,
        "error": None,
    }

    if triton_client is not None:
        try:
            triton_health["server_ready"] = bool(triton_client.is_server_ready())
            triton_health["model_ready"] = bool(triton_client.is_model_ready(TRITON_MODEL_NAME))
        except Exception as e:
            triton_health["error"] = str(e)
    else:
        triton_health["error"] = "Triton client is not initialized"

    with gallery_lock:
        embedding_shape = list(gallery_embeddings.shape) if hasattr(gallery_embeddings, "shape") else []
        gallery_count = len(gallery_ids)
        embedding_count = int(gallery_embeddings.shape[0]) if gallery_embeddings.ndim > 0 else 0
        gallery_health = {
            "count": gallery_count,
            "data_count": len(gallery_data),
            "embedding_count": embedding_count,
            "embedding_shape": embedding_shape,
            "loaded": gallery_count > 0,
            "consistent": len(gallery_data) == gallery_count == embedding_count,
        }

    is_healthy = (
        triton_health["server_ready"]
        and triton_health["model_ready"]
        and gallery_health["consistent"]
    )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "api": "healthy",
        "triton": triton_health,
        "gallery": gallery_health,
    }
