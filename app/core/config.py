import os

# --- Base Project Directory ---
BASE_DIR = os.getcwd()

# --- Data Directories ---
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_LFW_DIR = os.path.join(DATA_DIR, "lfw", "lfw-deepfunneled", "lfw-deepfunneled")
DEMO_DATA_DIR = os.path.join(DATA_DIR, "demo_data")

# --- Final Setup Directories (System Data) ---
FINAL_SETUP_DIR = os.path.join(DATA_DIR, "final_setup")
GALLERY_DIR = os.path.join(FINAL_SETUP_DIR, "gallery")
PROBE_DIR = os.path.join(FINAL_SETUP_DIR, "probe")

# --- Database and Embeddings Paths ---
SYSTEM_DB_PATH = os.path.join(FINAL_SETUP_DIR, "system_db.csv")
EMBEDDINGS_PATH = os.path.join(FINAL_SETUP_DIR, "gallery_embeddings.npy")

# --- Outputs ---
QR_CODES_DIR = os.path.join(BASE_DIR, "qr_codes")

# --- Model Settings ---
CHECKPOINTS_DIR = os.path.join(BASE_DIR, "checkpoints")
ONNX_MODEL_PATH = os.path.join(CHECKPOINTS_DIR, "edgeface_base.onnx")

# --- Application Constants ---
VERIFICATION_THRESHOLD = 0.5

# --- Server Defaults ---
APP_HOST = "127.0.0.1"
APP_PORT = 8080
