"""
Kavach Setu - Signature Verification API
Simple Flask API for signature comparison using Gemini
Takes 2 cropped signature image paths and returns similarity score
"""

from flask import Flask, request, jsonify
import os
import numpy as np
import cv2
from PIL import Image, ImageOps
from google.genai import Client as GeminiClient
from google.genai import types
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# GCP Configuration (REPLACE WITH YOUR ACTUAL VALUES)
PROJECT_ID = ""
VERTEXAI_LOCATION = ""
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Comparison threshold
MATCH_THRESHOLD = 80


# ============================================================================
# SIGNATURE PREPROCESSING
# ============================================================================

def preprocess_signature(pil_image: Image.Image) -> Image.Image:
    """
    Preprocesses signature image for Gemini analysis.
    - Denoising to clean artifacts
    - Auto-contrast for better visibility
    - Standardized resizing
    """
    # 1. Convert to grayscale
    img = pil_image.convert("L")
    img_cv = np.array(img)

    # 2. Denoising (removes scanner artifacts)
    img_cv = cv2.fastNlMeansDenoising(img_cv, None, 10, 7, 21)
    img = Image.fromarray(img_cv)

    # 3. Auto-contrast boost
    img = ImageOps.autocontrast(img)

    # 4. Standardized resizing
    img = img.resize((400, 150), resample=Image.Resampling.LANCZOS)

    # 5. Return as RGB (required for Gemini)
    return img.convert("RGB")


# ============================================================================
# GEMINI SIGNATURE COMPARISON
# ============================================================================

def analyze_signatures_with_gemini(sig1_pil: Image.Image, sig2_pil: Image.Image) -> tuple[int, str]:
    """
    Compares two signature images using Gemini multimodal model.
    Returns: (similarity_score, detailed_analysis)
    """

    if sig1_pil is None or sig2_pil is None:
        return 0, "Missing one or both signature images."

    try:
        # Initialize Gemini client
        client = GeminiClient(
            vertexai=True,
            project=PROJECT_ID,
            location=VERTEXAI_LOCATION
        )

        # Preprocess signatures
        img1 = preprocess_signature(sig1_pil)
        img2 = preprocess_signature(sig2_pil)

        # System instruction for forensic analysis
        system_instruction = (
            "You are a highly specialized forensic handwriting expert for signature verification. "
            "Your primary task is to assess if the two signatures were produced by the same individual. "
            "**STRICTLY IGNORE ALL COLOR, BACKGROUND TINTS, AND IMAGE NOISE.** "
            "Focus **ONLY** on **writer-invariant biometric traits**: stroke construction, rhythm, "
            "connection points, and proportional sizing of individual letterforms. "
            "The Similarity Score (0-100) must ONLY reflect the biometric writing style consistency. "
            "A score of **80+** is reserved for a high confidence match based on consistent style. "
            "A score of **under 20** is reserved for clear stylistic differences (different writer)."
        )

        # Prompt with images
        prompt_contents = [
            img1,
            "Signature 1.",
            img2,
            "Signature 2.",
            "Compare Signature 1 and Signature 2. Provide the analysis in a single Markdown block "
            "using **only** the following two fields. Do not add any extra text, characters, or formatting to the score line."
            "\n\n**Similarity Score:** [X/100]"
            "\n**Analysis:** [Detailed written analysis of consistency/inconsistency, focusing on biometric traits.]"
        ]

        # Generate content
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt_contents,
            config=types.GenerateContentConfig(
                temperature=0.10,  # Low temperature for determinism
                system_instruction=system_instruction
            )
        )

        # Parse response
        analysis = response.text
        score = 0

        # Extract score using regex
        robust_pattern = r'similarity\s*score.*?(\d+)\s*/\s*100'
        match = re.search(robust_pattern, analysis, re.IGNORECASE | re.DOTALL)

        if match:
            score = int(match.group(1).strip())

        return score, analysis

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return 0, f"API error occurred: {e}"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/verify', methods=['POST'])
def verify_signatures():
    """
    Main signature verification endpoint.

    Request JSON:
    {
        "signature1_path": "path/to/signature1.png",
        "signature2_path": "path/to/signature2.png"
    }

    Response JSON:
    {
        "status": "success",
        "match": true/false,
        "similarity_score": 85,
        "threshold": 80,
        "analysis": "Detailed analysis text...",
        "message": "HIGH CONFIDENCE MATCH" or "POTENTIAL MISMATCH"
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

        sig1_path = data.get('signature1_path')
        sig2_path = data.get('signature2_path')

        # Validate inputs
        if not sig1_path or not sig2_path:
            return jsonify({
                "status": "error",
                "message": "Both signature1_path and signature2_path are required"
            }), 400

        # Check if files exist
        if not os.path.exists(sig1_path):
            return jsonify({
                "status": "error",
                "message": f"Signature 1 file not found: {sig1_path}"
            }), 404

        if not os.path.exists(sig2_path):
            return jsonify({
                "status": "error",
                "message": f"Signature 2 file not found: {sig2_path}"
            }), 404

        # Load images
        try:
            sig1_pil = Image.open(sig1_path)
            sig2_pil = Image.open(sig2_path)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to load images: {str(e)}"
            }), 400

        # Perform comparison
        logging.info(f"Comparing signatures: {sig1_path} vs {sig2_path}")
        similarity_score, analysis = analyze_signatures_with_gemini(sig1_pil, sig2_pil)

        # Determine match result
        is_match = similarity_score >= MATCH_THRESHOLD
        message = "HIGH CONFIDENCE MATCH" if is_match else "POTENTIAL MISMATCH"

        # Prepare response
        response = {
            "status": "success",
            "match": is_match,
            "similarity_score": similarity_score,
            "threshold": MATCH_THRESHOLD,
            "analysis": analysis,
            "message": message,
            "signature1_path": sig1_path,
            "signature2_path": sig2_path
        }

        logging.info(f"Verification result: Score={similarity_score}, Match={is_match}")

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
        "service": "Signature Verification API",
        "model": GEMINI_MODEL_NAME
    }), 200


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🖊️  Kavach Setu - Signature Verification API")
    print("=" * 70)
    print("\n📋 Configuration:")
    print(f"  • Project ID: {PROJECT_ID}")
    print(f"  • Model: {GEMINI_MODEL_NAME}")
    print(f"  • Match Threshold: {MATCH_THRESHOLD}")
    print("\n📋 Available Endpoints:")
    print("  • POST /verify - Compare two signature images")
    print("  • GET  /health - Health check")
    print("\n🚀 Server starting on http://localhost:5000")
    print("=" * 70)
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
