import logging
import json

import cv2
import numpy as np
import tritonclient.grpc as grpcclient
from PIL import Image

from edgeface.face_alignment import align

logger = logging.getLogger(__name__)


def preprocess_image(aligned_img):
    img_ndarray = np.array(aligned_img).astype(np.float32) / 255.0
    img_ndarray = np.transpose(img_ndarray, (2, 0, 1))
    img_ndarray = (img_ndarray - 0.5) / 0.5
    img_ndarray = np.expand_dims(img_ndarray, axis=0)
    return img_ndarray


def extract_embedding(image_bytes, session, input_name):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        logger.error("Could not decode image bytes into an OpenCV image.")
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)

    aligned_face = align.get_aligned_face(image_path=None, rgb_pil_image=pil_img)
    if aligned_face is None:
        logger.warning("Warning: Could not detect/align face")
        return None

    input_tensor = preprocess_image(aligned_face)
    outputs = session.run(None, {input_name: input_tensor})
    embedding = outputs[0][0]

    norm = np.linalg.norm(embedding)
    if norm == 0 or np.isnan(norm):
        logger.error(f"Invalid embedding norm: {norm}")
        return None
    return embedding / norm


def extract_embedding_from_triton(image_bytes, triton_client, model_name="face_matching_model"):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        logger.error("Could not decode image bytes into an OpenCV image.")
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)

    aligned_face = align.get_aligned_face(image_path=None, rgb_pil_image=pil_img)
    if aligned_face is None:
        logger.warning("Warning: Could not detect/align face")
        return None

    if triton_client is None:
        logger.error("Triton client is not initialized; cannot extract embedding from Triton.")
        return None

    input_tensor = preprocess_image(aligned_face)
    triton_input = grpcclient.InferInput("input", input_tensor.shape, "FP32")
    triton_input.set_data_from_numpy(input_tensor.astype(np.float32))

    requested_output = grpcclient.InferRequestedOutput("output")
    try:
        response = triton_client.infer(model_name=model_name, inputs=[triton_input], outputs=[requested_output])
        embedding = response.as_numpy("output")
        if embedding is None:
            logger.error("Triton response did not contain the expected output tensor 'output'.")
            return None
        if embedding.ndim == 2 and embedding.shape[0] == 1:
            embedding = embedding[0]
        if embedding.size == 0:
            logger.error("Triton returned an empty embedding array.")
            return None

        embedding = embedding.astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0 or np.isnan(norm):
            logger.error(f"Invalid Triton embedding norm: {norm}")
            return None
        return embedding / norm
    except Exception as e:
        logger.error(f"Error occurred while inferring with Triton: {e}")
        return None


def load_gallery_data(supabase_client):
    logger.info("Loading gallery data from Supabase...")
    try:
        # Supabase has a default limit of 1000 rows, so we need to paginate
        all_users = []
        page_size = 1000
        offset = 0

        while True:
            response = supabase_client.table("face_users").select("id, name, embedding").range(offset, offset + page_size - 1).execute()
            users = response.data

            if not users:
                break

            all_users.extend(users)
            offset += page_size

            # Safety check to prevent infinite loops
            if len(users) < page_size:
                break

        logger.info(f"Total users fetched from Supabase: {len(all_users)}")

        if not all_users:
            logger.info("No users found in Supabase. Starting with an empty gallery.")
            return {}, [], np.array([])

        gallery_data = {}
        gallery_embeddings_list = []
        gallery_ids = []

        for user in sorted(all_users, key=lambda x: x['id']):
            person_id = f"{int(user['id']):06d}"
            gallery_ids.append(person_id)
            embedding = np.array(json.loads(user['embedding'])) if user['embedding'] else None
            if embedding is not None:
                gallery_embeddings_list.append(embedding)
                gallery_data[person_id] = {'name': user['name'], 'embedding': embedding}

        gallery_embeddings = np.array(gallery_embeddings_list) if gallery_embeddings_list else np.array([])
        logger.info(f"Successfully loaded {len(gallery_ids)} people from Supabase into memory.")
        return gallery_data, gallery_ids, gallery_embeddings
    except Exception as e:
        logger.error(f"Error loading gallery data from Supabase: {e}. Starting with an empty gallery.")
        return {}, [], np.array([])
