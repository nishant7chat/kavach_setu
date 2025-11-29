"""
Test script for Face Verification API
Tests the API with sample face images from face/Image_folder/Image_folder
"""

import requests
import json
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:5001/verify"
HEALTH_URL = "http://localhost:5001/health"

# Sample image paths
BASE_PATH = r"C:\Users\kavita.jain\Documents\Kavach_Setu_Face_Sign\face\Image_folder\Image_folder"

# Test cases
TEST_CASES = [
    {
        "name": "Test Case 1: Aadhaar vs Selfie (Same Person)",
        "img1": os.path.join(BASE_PATH, "aadhar.jpg"),
        "img2": os.path.join(BASE_PATH, "selfie.jpg"),
        "expected": "MATCH"
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_json(data, title=None):
    """Pretty print JSON data"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def check_health():
    """Check if API server is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        if response.status_code == 200:
            print("✅ API Server is running")
            print_json(response.json(), "Health Check Response")
            return True
        else:
            print("⚠️  API Server returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: API Server is not running!")
        print("   Please start the server first:")
        print("   $ python face_verification_api.py")
        return False


def test_face_verification(test_case):
    """Test face verification for a given test case"""

    print_header(test_case["name"])

    # Check if files exist
    if not os.path.exists(test_case["img1"]):
        print(f"❌ Image 1 not found: {test_case['img1']}")
        return

    if not os.path.exists(test_case["img2"]):
        print(f"❌ Image 2 not found: {test_case['img2']}")
        return

    print(f"\n📄 Image 1: {os.path.basename(test_case['img1'])}")
    print(f"📄 Image 2: {os.path.basename(test_case['img2'])}")
    print(f"🎯 Expected Result: {test_case['expected']}")

    # Prepare request
    payload = {
        "image1_path": test_case["img1"],
        "image2_path": test_case["img2"]
    }

    print_json(payload, "\n📤 Request Payload")

    try:
        # Make API call
        print("\n⏳ Calling API... (This may take 5-10 seconds for first run)")
        response = requests.post(API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print_json(result, "\n📥 Response")

            # Display results
            print("\n" + "=" * 80)
            print("  VERIFICATION RESULTS")
            print("=" * 80)

            score = result.get("similarity_score", 0.0)
            face_match = result.get("face_match", False)
            threshold = result.get("threshold", 0.45)
            confidence = result.get("confidence_level", "UNKNOWN")

            # Color coding for console
            if face_match:
                print(f"\n✅ Result: {result.get('message', 'MATCH')}")
                print(f"🎯 Similarity Score: {score:.2%} (Threshold: {threshold:.2%})")
                print(f"📊 Confidence Level: {confidence}")
            else:
                print(f"\n❌ Result: {result.get('message', 'MISMATCH')}")
                print(f"🎯 Similarity Score: {score:.2%} (Threshold: {threshold:.2%})")
                print(f"📊 Confidence Level: {confidence}")

            # Technical details
            print("\n🔧 Technical Details:")
            print(f"   • Model: {result.get('model_used', 'N/A')}")
            print(f"   • Detector: {result.get('detector_used', 'N/A')}")
            print(f"   • Distance Metric: {result.get('distance_metric', 'N/A')}")

            # Check if result matches expectation
            expected_match = test_case["expected"] == "MATCH"
            if face_match == expected_match:
                print(f"\n✅ Test PASSED: Result matches expected ({test_case['expected']})")
            else:
                print(f"\n⚠️  Test FAILED: Expected {test_case['expected']}, got {'MATCH' if face_match else 'MISMATCH'}")

        else:
            print(f"\n❌ API Error: Status {response.status_code}")
            print_json(response.json(), "Error Response")

    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timeout (API took too long to respond)")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all test cases"""

    print("\n")
    print("👤" * 40)
    print("     FACE VERIFICATION API - TEST SUITE")
    print("👤" * 40)

    # Check server health
    print_header("Health Check")
    if not check_health():
        return

    # Check if sample images exist
    print_header("Checking Sample Images")
    print(f"\n📂 Base Path: {BASE_PATH}")

    aadhar_path = os.path.join(BASE_PATH, "aadhar.jpg")
    selfie_path = os.path.join(BASE_PATH, "selfie.jpg")

    if os.path.exists(aadhar_path):
        print(f"✅ Found: aadhar.jpg")
    else:
        print(f"❌ Missing: aadhar.jpg")

    if os.path.exists(selfie_path):
        print(f"✅ Found: selfie.jpg")
    else:
        print(f"❌ Missing: selfie.jpg")

    # Run test cases
    for test_case in TEST_CASES:
        test_face_verification(test_case)

    # Summary
    print_header("TEST SUMMARY")
    print("\n✅ All tests completed!")
    print(f"\n📊 Test Cases Run: {len(TEST_CASES)}")
    print("\n📝 Notes:")
    print("   • Similarity threshold: 0.45 (45%)")
    print("   • Model: ArcFace (best for face verification)")
    print("   • Detector: RetinaFace (best face detector)")
    print("   • High confidence: 70%+, Moderate: 45-70%, Low: <45%")
    print()


if __name__ == '__main__':
    main()
