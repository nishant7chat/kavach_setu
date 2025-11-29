import streamlit as st
import os
import io
import numpy as np
import cv2 
from PIL import Image, ImageOps, ImageEnhance
from google.cloud import documentai_v1 as documentai
from google.genai import Client as GeminiClient
from google.genai import types
import re 

# Set up basic logging
import logging
logging.basicConfig(level=logging.INFO)

# ===============================================
# 1. CONFIGURATION AND SETUP
# ===============================================

# --- 1a. GCP Base Configuration (REPLACE WITH YOUR ACTUAL VALUES) ---
PROJECT_ID = "prj-dt-aicoe-idfc"
LOCATION = "us" 
VERTEXAI_LOCATION = "us-central1" 

RTO_PROCESSOR_ID = "764f1185e645e478"
PAN_PROCESSOR_ID = "2aae5f384ee31fab"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# --- 1b. Document Entity Names (Must match your DocAI labeler) ---
RTO_ENTITY_NAME = "signature1"
PAN_ENTITY_NAME = "pan_signature" 

# --- 1c. Comparison Parameters ---
GEMINI_MATCH_THRESHOLD = 80 

# ===============================================
# 2. GEMINI MULTI-MODAL ANALYSIS (Vertex AI)
# ===============================================

def preprocess_signature_gemini(pil_image: Image.Image) -> Image.Image:
    """
    Minimal preprocessing: Focus on Denoising and Autocontrast 
    without destructive thresholding to preserve pen pressure and flow details.
    """
    # 1. Convert to grayscale and NumPy array
    img = pil_image.convert("L")
    img_cv = np.array(img)
    
    # 2. Denoising (Crucial for cleaning up scanner/DocAI artifacts)
    img_cv = cv2.fastNlMeansDenoising(img_cv, None, 10, 7, 21)
    img = Image.fromarray(img_cv)
    
    # 3. Light Contrast (Autocontrast is the safest boost)
    img = ImageOps.autocontrast(img)
    
    # 4. Standardized Resizing (consistent input shape for the model)
    img = img.resize((400, 150), resample=Image.Resampling.LANCZOS)
    
    # Return as RGB (required for robust Gemini multi-modal input)
    return img.convert("RGB") 

@st.cache_data(show_spinner="Running Forensic Analysis with Gemini on Vertex AI...")
def analyze_signatures_with_gemini(rto_pil_img: Image.Image, pan_pil_img: Image.Image) -> tuple[int, str, str]:
    """Sends two preprocessed PIL Image objects to the Gemini model for forensic comparison."""
    
    if rto_pil_img is None or pan_pil_img is None:
         return 0, "Missing one or both signature images.", "Gemini Error"

    try:
        # Initialize the client for Vertex AI
        client = GeminiClient(
            vertexai=True,
            project=PROJECT_ID,
            location=VERTEXAI_LOCATION
        )
        
        # 1. Apply Gemini-specific preprocessing
        img_rto = preprocess_signature_gemini(rto_pil_img)
        img_pan = preprocess_signature_gemini(pan_pil_img)

        # 2. FINAL System Instruction: Hyper-Focused on Ink Path and Style
        system_instruction = (
            "You are a highly specialized forensic handwriting expert for off-line signature verification. "
            "Your primary task is to assess if the two signatures were produced by the same individual. "
            "**STRICTLY IGNORE ALL COLOR, BACKGROUND TINTS (e.g., blue), AND IMAGE NOISE.** "
            "Focus **ONLY** on **writer-invariant biometric traits**: stroke construction, rhythm, connection points, and proportional sizing of individual letterforms. "
            "The Similarity Score (0-100) must ONLY reflect the biometric writing style consistency. "
            "A score of **80+** is reserved for a high confidence match based on consistent style. "
            "A score of **under 20** is reserved for clear stylistic differences (different writer)."
        )

        # 3. Define the User Content (Images + Request)
        prompt_contents = [
            img_rto, 
            "Signature 1 (RTO Document).",
            img_pan,
            "Signature 2 (PAN Document).",
            "Compare Signature 1 and Signature 2. Provide the analysis in a single Markdown block "
            "using **only** the following two fields. Do not add any extra text, characters, or formatting to the score line."
            "\n\n**Similarity Score:** [X/100]"
            "\n**Analysis:** [Detailed written analysis of consistency/inconsistency, focusing on biometric traits.]"
        ]

        # 4. Generate Content
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt_contents,
            config=types.GenerateContentConfig(
                temperature=0.10, # Lowered for maximum determinism and adherence to the prompt
                system_instruction=system_instruction
            )
        )
        
        # 5. Parse the score and analysis from the response using RegEx (ROBUST LOGIC)
        analysis = response.text
        score = 0 
        
        # Highly robust RegEx: looks for "similarity score" then extracts the first group of digits followed by /100.
        robust_pattern = r'similarity\s*score.*?(\d+)\s*/\s*100'
        match = re.search(robust_pattern, analysis, re.IGNORECASE | re.DOTALL)
        
        if match:
            try:
                score = int(match.group(1).strip())
                status_message = "Gemini Analysis Success (Score Parsed)"
            except ValueError:
                status_message = "Gemini Analysis Success (Parsing Error: Non-numeric score)"
        else:
             status_message = "Gemini Analysis Success (Parsing Error: Score format not found)"

        return score, analysis, status_message

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return 0, f"An API error occurred: {e}", "Gemini API Error"

# ===============================================
# 3. DOCUMENT AI EXTRACTION
# ===============================================

def get_mime_type(file_name):
    """Determines the correct MIME type based on file extension."""
    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.pdf': return 'application/pdf'
    if ext in ['.jpg', '.jpeg']: return 'image/jpeg'
    if ext == '.png': return 'image/png'
    return 'application/pdf'

@st.cache_data(show_spinner="Extracting signature with Document AI...")
def extract_signature_from_upload(uploaded_file, doc_type):
    """Processes file via Document AI and extracts the cropped PIL image."""
    processor_id = RTO_PROCESSOR_ID if doc_type == "RTO" else PAN_PROCESSOR_ID
    entity_name = RTO_ENTITY_NAME if doc_type == "RTO" else PAN_ENTITY_NAME
    
    client = documentai.DocumentProcessorServiceClient()
    processor_name = client.processor_path(PROJECT_ID, LOCATION, processor_id)
    
    uploaded_file.seek(0)
    document_content = uploaded_file.read()
    mime_type = get_mime_type(uploaded_file.name)
    
    try:
        raw_document = documentai.RawDocument(content=document_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document

        best_entity = None
        max_confidence = -1.0
        
        for entity in document.entities:
            if entity.type_ == entity_name and entity.confidence > max_confidence:
                if entity.page_anchor and entity.page_anchor.page_refs:
                    max_confidence = entity.confidence
                    best_entity = entity
        
        if best_entity:
            # Cropping Logic
            page_ref = best_entity.page_anchor.page_refs[0] 
            bbox_poly = getattr(page_ref, 'bounding_poly', None)
            
            if not bbox_poly or not bbox_poly.normalized_vertices:
                st.error(f"Signature entity '{entity_name}' found but bounding box is missing.")
                return None

            bbox_norm = bbox_poly.normalized_vertices
            page_index = page_ref.page
            
            docai_page = document.pages[page_index]
            image_bytes = docai_page.image.content
            page_image = Image.open(io.BytesIO(image_bytes))
            width, height = page_image.size
            
            # Get min/max normalized coordinates and apply padding
            padding = 10
            x_min = min(v.x for v in bbox_norm)
            y_min = min(v.y for v in bbox_norm)
            x_max = max(v.x for v in bbox_norm)
            y_max = max(v.y for v in bbox_norm)
            
            x0 = max(0, int(x_min * width) - padding)
            y0 = max(0, int(y_min * height) - padding)
            x1 = min(width, int(x_max * width) + padding)
            y1 = min(height, int(y_max * height) + padding)

            cropped_sig_pil = page_image.crop((x0, y0, x1, y1))
            
            return cropped_sig_pil
        
        st.error(f"Signature entity '{entity_name}' not found in {doc_type} document.")
        return None

    except Exception as e:
        logging.error(f"Document AI error for {doc_type}: {e}")
        st.error(f"Document AI error for {doc_type}: {e}")
        return None

# ===============================================
# 4. STREAMLIT APP LAYOUT AND EXECUTION
# ===============================================

def main():
    st.set_page_config(layout="wide", page_title="Gemini Signature Verification")
    
    # st.title("🧾 RTO Signature Verification")
    # st.markdown("Extracts signatures using **Document AI** and performs **Forensic Analysis** using **Vertex AI Gemini**.")
    # --- IDFC Bank Themed Header ---
    # --- Corporate Blue Themed Header (IDFC Enterprise Style) ---
    st.markdown(
        """
        <style>
            /* Modern Blue Theme */
            .main-header {
                background: linear-gradient(90deg, #004AAD, #0078D7);
                color: white;
                padding: 25px 0;
                border-radius: 12px;
                text-align: center;
                font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-weight: 700;
                font-size: 28px;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .emoji {
                font-size: 32px;
                vertical-align: middle;
                margin-right: 10px;
            }
        </style>
        <div class="main-header">
            <span class="emoji">📝</span> RTO Signature Verification
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # --- File Upload Columns ---
    col1, col2 = st.columns(2)
    rto_sig_pil = None
    pan_sig_pil = None

    with col1:
        st.header("📄 RTO Form")
        rto_file = st.file_uploader(
            "Upload RTO Form (PDF/Image)", 
            type=["pdf", "jpg", "jpeg", "png"], 
            key="rto_uploader"
        )
        if rto_file:
            rto_sig_pil = extract_signature_from_upload(rto_file, "RTO")
            if rto_sig_pil:
                st.subheader("Extracted RTO Signature")
                st.image(rto_sig_pil, caption="RTO Signature", use_column_width=True)

    with col2:
        st.header("💳 PAN Card")
        pan_file = st.file_uploader(
            "Upload PAN Card (Image/PDF)", 
            type=["jpg", "jpeg", "png", "pdf"], 
            key="pan_uploader"
        )
        if pan_file:
            pan_sig_pil = extract_signature_from_upload(pan_file, "PAN")
            if pan_sig_pil:
                st.subheader("Extracted PAN Signature")
                st.image(pan_sig_pil, caption="PAN Signature", use_column_width=True)

    st.markdown("---")

    # --- Comparison Section ---
    st.header("3. Verification Results")
    
    if rto_sig_pil is not None and pan_sig_pil is not None:
        
        if st.button("▶️ Run Forensic Comparison", type="primary"):
            
            gemini_score, gemini_analysis, gemini_status = analyze_signatures_with_gemini(rto_sig_pil, pan_sig_pil)
            is_match_gemini = gemini_score >= GEMINI_MATCH_THRESHOLD
            
            st.subheader("Gemini Multi-modal Analysis")
            
            if is_match_gemini:
                st.success("✅ Signature Verification: **HIGH CONFIDENCE MATCH**")
                color = "green"
            else:
                st.error("⚠️ Signature Verification: **POTENTIAL MISMATCH**")
                color = "red"
            
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid {color};">
                    <h4 style="color: black; margin-top: 0px;">Forensic Similarity Score (0-100)</h4>
                    <h1 style="color: {color}; font-size: 50px; margin-bottom: 0px;">{gemini_score}</h1>
                    <p>Match Threshold: {GEMINI_MATCH_THRESHOLD}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            with st.expander("🔍 AI Detailed Analysis"):
                st.markdown(gemini_analysis)
                st.write(f"**Status:** {gemini_status}")
                st.write("---")
                st.write("The analysis is based on enhanced preprocessing and a system instruction specifically designed to ignore background noise.")

    else:
        st.info("⬆️ Please upload both the RTO Form and the PAN Card to run the verification.")

if __name__ == "__main__":
    main()
