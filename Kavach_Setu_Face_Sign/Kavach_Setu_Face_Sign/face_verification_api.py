"""
Kavach Setu - Face Verification API
Simple Flask API for face matching using DeepFace
Takes 2 face image paths and returns similarity score
"""

from flask import Flask, request, jsonify
import os
from deepface import DeepFace
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Suppress TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

app = Flask(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Face matching threshold (0.45 = 45% similarity for match)
MATCH_THRESHOLD = 0.45

# DeepFace model configuration
MODEL_NAME = "ArcFace"  # Best for face verification
DETECTOR_BACKEND = "opencv"  # Most stable detector (changed from retinaface due to tuple error)
DISTANCE_METRIC = "cosine"  # Cosine distance for similarity


# ============================================================================
# FACE VERIFICATION LOGIC
# ============================================================================

def verify_faces(image1_path: str, image2_path: str) -> dict:
    """
    Compares two face images using DeepFace.

    Args:
        image1_path: Path to first face image
        image2_path: Path to second face image

    Returns:
        dict with face_match, similarity_score, and model info
    """
    try:
        # Validate images exist and are readable
        import cv2
        import numpy as np

        # Try to load images with OpenCV to ensure they're valid
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        if img1 is None:
            raise ValueError(f"Failed to load image 1: {image1_path}")
        if img2 is None:
            raise ValueError(f"Failed to load image 2: {image2_path}")

        # Check if images are tuples (common error)
        if isinstance(img1, tuple):
            logging.error(f"Image 1 loaded as tuple instead of array")
            raise ValueError("Image 1 format error - loaded as tuple")
        if isinstance(img2, tuple):
            logging.error(f"Image 2 loaded as tuple instead of array")
            raise ValueError("Image 2 format error - loaded as tuple")

        logging.info(f"Image 1 shape: {img1.shape}, Image 2 shape: {img2.shape}")

        # Run DeepFace verification with fallback detectors
        detectors_to_try = [DETECTOR_BACKEND, "ssd", "mtcnn", "skip"]
        result = None
        last_error = None

        for detector in detectors_to_try:
            try:
                logging.info(f"Trying detector: {detector}")
                result = DeepFace.verify(
                    img1_path=image1_path,
                    img2_path=image2_path,
                    model_name=MODEL_NAME,
                    detector_backend=detector,
                    distance_metric=DISTANCE_METRIC,
                    enforce_detection=False,  # Don't fail if face not detected
                )
                logging.info(f"Success with detector: {detector}")
                break  # Success! Stop trying
            except Exception as e:
                last_error = e
                logging.warning(f"Detector {detector} failed: {str(e)}")
                continue

        if result is None:
            raise Exception(f"All detectors failed. Last error: {last_error}")

        # Calculate similarity score (1 - distance)
        # DeepFace returns distance (0 = identical, 1 = different)
        # We convert to similarity (1 = identical, 0 = different)
        similarity_score = round(1 - result["distance"], 4)

        # Determine if faces match based on threshold
        face_match = similarity_score >= MATCH_THRESHOLD

        return {
            "face_match": face_match,
            "similarity_score": similarity_score,
            "threshold": MATCH_THRESHOLD,
            "model_used": result.get("model", MODEL_NAME),
            "detector_used": DETECTOR_BACKEND,
            "distance_metric": DISTANCE_METRIC
        }

    except Exception as e:
        logging.error(f"Face verification error: {e}")
        return {
            "face_match": False,
            "similarity_score": 0.0,
            "threshold": MATCH_THRESHOLD,
            "error": str(e)
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/verify', methods=['POST'])
def verify_face_match():
    """
    Main face verification endpoint.

    Request JSON:
    {
        "image1_path": "path/to/face1.jpg",
        "image2_path": "path/to/face2.jpg"
    }

    Response JSON:
    {
        "status": "success",
        "face_match": true/false,
        "similarity_score": 0.87,
        "threshold": 0.45,
        "model_used": "ArcFace",
        "message": "FACES MATCH" or "FACES DO NOT MATCH"
    }
    """

    try:
        # Get request data
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400

        image1_path = data.get('image1_path')
        image2_path = data.get('image2_path')

        # Validate inputs
        if not image1_path or not image2_path:
            return jsonify({
                "status": "error",
                "message": "Both image1_path and image2_path are required"
            }), 400

        # Check if files exist
        if not os.path.exists(image1_path):
            return jsonify({
                "status": "error",
                "message": f"Image 1 file not found: {image1_path}"
            }), 404

        if not os.path.exists(image2_path):
            return jsonify({
                "status": "error",
                "message": f"Image 2 file not found: {image2_path}"
            }), 404

        # Verify images can be loaded
        try:
            Image.open(image1_path)
            Image.open(image2_path)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to load images: {str(e)}"
            }), 400

        # Perform face verification
        logging.info(f"Verifying faces: {image1_path} vs {image2_path}")
        result = verify_faces(image1_path, image2_path)

        # Check if error occurred
        if "error" in result:
            return jsonify({
                "status": "error",
                "message": result["error"],
                "face_match": False,
                "similarity_score": 0.0
            }), 500

        # Determine match message
        face_match = result["face_match"]
        similarity_score = result["similarity_score"]

        if face_match:
            message = "FACES MATCH"
            confidence = "HIGH CONFIDENCE" if similarity_score >= 0.70 else "MODERATE CONFIDENCE"
        else:
            message = "FACES DO NOT MATCH"
            confidence = "LOW CONFIDENCE"

        # Prepare response
        response = {
            "status": "success",
            "face_match": face_match,
            "similarity_score": similarity_score,
            "threshold": result["threshold"],
            "model_used": result["model_used"],
            "detector_used": result["detector_used"],
            "distance_metric": result["distance_metric"],
            "message": message,
            "confidence_level": confidence,
            "image1_path": image1_path,
            "image2_path": image2_path
        }

        logging.info(f"Verification result: Score={similarity_score}, Match={face_match}")

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Verification error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Face Verification API",
        "model": MODEL_NAME,
        "detector": DETECTOR_BACKEND,
        "threshold": MATCH_THRESHOLD
    }), 200


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("👤 Kavach Setu - Face Verification API")
    print("=" * 70)
    print("\n📋 Configuration:")
    print(f"  • Model: {MODEL_NAME}")
    print(f"  • Detector: {DETECTOR_BACKEND}")
    print(f"  • Distance Metric: {DISTANCE_METRIC}")
    print(f"  • Match Threshold: {MATCH_THRESHOLD}")
    print("\n📋 Available Endpoints:")
    print("  • POST /verify - Compare two face images")
    print("  • GET  /health - Health check")
    print("\n🚀 Server starting on http://localhost:5001")
    print("=" * 70)
    print()

    app.run(host='0.0.0.0', port=5001, debug=True)
