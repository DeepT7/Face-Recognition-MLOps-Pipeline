import os
import sys
import argparse
import numpy as np
from torchvision import transforms
import onnxruntime as ort
import pandas as pd
from PIL import Image
import logging
from app.utils import preprocess_image

# Add the root project directory to sys.path so 'face_alignment' can be found
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edgeface')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from edgeface.face_alignment import align
transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_embeddings(onnx_model_path, gallery_dir, output_path, db_file):
    logger.info(f"Loading ONNX model from {onnx_model_path}...")
    # Use CPUExecutionProvider, or add 'CUDAExecutionProvider' for GPU
    session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    logger.info(f"Model input name: {input_name}")
    
    embeddings_dict = {}
    
    logger.info(f"Loading database from {db_file}...")
    df = pd.read_csv(db_file, dtype={'person_id': str})
    base_dir = os.path.dirname(db_file)

    logger.info(f"Extracting embeddings from gallery: {gallery_dir}")
    # Iterate through the database rows to ensure we process each registered person
    for index, row in df.iterrows():
        person_id = str(row['person_id']).zfill(6)
        person_name = row['person_name']
        # Construct the full path to the image
        img_path = os.path.join(base_dir, row['gallery_path'])

        # 1. Align face
        aligned_face = align.get_aligned_face(img_path)
        if aligned_face is None:
            logger.warning(f"Warning: Could not detect/align face in {img_path}")
            continue
            
        # 2. Preprocess
        input_tensor = preprocess_image(aligned_face)
        # Or using torchvision.transform 
        # input_tensor = transforms(aligned_face)
        # input_tensor = input_tensor.unsqueeze(0) # Add batch dimension
        
        # 3. Extract embedding
        outputs = session.run(None, {input_name: input_tensor})
        embedding = outputs[0][0] # Remove batch dimension
        
        # 4. L2 Normalize the embedding (best practice for face recognition tasks)
        embedding = embedding / np.linalg.norm(embedding)
        
    
        embeddings_dict[person_id] = {
            'name': person_name,
            'embedding': embedding
        }
        logger.info(f"Processed: {person_id} ({person_name})")
        
    # Save to disk
    np.save(output_path, embeddings_dict)
    
    logger.info(f"Finished! Saved {len(embeddings_dict)} embeddings to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract face embeddings using EdgeFace ONNX model.")
    parser.add_argument("--onnx_model", type=str, required=True, help="Path to the .onnx model file")
    parser.add_argument("--gallery_dir", type=str, default="data/final_setup/gallery", help="Path to gallery directory")
    parser.add_argument("--output_file", type=str, default="data/final_setup/gallery_embeddings.npy", help="Path to save the .npy file")
    parser.add_argument("--db_file", type=str, default="data/final_setup/system_db.csv", help="Path to the system database CSV")
    args = parser.parse_args()
    extract_embeddings(args.onnx_model, args.gallery_dir, args.output_file, args.db_file)