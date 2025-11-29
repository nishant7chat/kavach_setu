"""
Test script for Signature Verification API
Tests the API with sample signature images from signature/main_app folder
"""

import requests
import json
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:5000/verify"
HEALTH_URL = "http://localhost:5000/health"

# Sample image paths (adjust if your images are in different location)
BASE_PATH = r"C:\Workarea\Adhish\task\Kavach Setu\signature\main_app"

# Test pairs
TEST_CASES = [
    {
        "name": "Test Case 1: Genuine Match (sign_og.png vs sign_og_true.png)",
        "sig1": os.path.join(BASE_PATH, "sign_og.png"),
        "sig2": os.path.join(BASE_PATH, "sign_og_true.png"),
        "expected": "MATCH"
    },
    {
        "name": "Test Case 2: Forgery Detection (sign_og.png vs sign_forged.png)",
        "sig1": os.path.join(BASE_PATH, "sign_og.png"),
        "sig2": os.path.join(BASE_PATH, "sign_forged.png"),
        "expected": "MISMATCH"
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
        print("   $ python signature_verification_api.py")
        return False


def test_signature_verification(test_case):
    """Test signature verification for a given test case"""

    print_header(test_case["name"])

    # Check if files exist
    if not os.path.exists(test_case["sig1"]):
        print(f"❌ Signature 1 not found: {test_case['sig1']}")
        return

    if not os.path.exists(test_case["sig2"]):
        print(f"❌ Signature 2 not found: {test_case['sig2']}")
        return

    print(f"\n📄 Signature 1: {os.path.basename(test_case['sig1'])}")
    print(f"📄 Signature 2: {os.path.basename(test_case['sig2'])}")
    print(f"🎯 Expected Result: {test_case['expected']}")

    # Prepare request
    payload = {
        "signature1_path": test_case["sig1"],
        "signature2_path": test_case["sig2"]
    }

    print_json(payload, "\n📤 Request Payload")

    try:
        # Make API call
        print("\n⏳ Calling API... (This may take 10-20 seconds)")
        response = requests.post(API_URL, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print_json(result, "\n📥 Response")

            # Display results
            print("\n" + "=" * 80)
            print("  VERIFICATION RESULTS")
            print("=" * 80)

            score = result.get("similarity_score", 0)
            is_match = result.get("match", False)
            threshold = result.get("threshold", 80)

            # Color coding for console
            if is_match:
                print(f"\n✅ Result: {result.get('message', 'MATCH')}")
                print(f"🎯 Similarity Score: {score}/100 (Threshold: {threshold})")
            else:
                print(f"\n⚠️  Result: {result.get('message', 'MISMATCH')}")
                print(f"🎯 Similarity Score: {score}/100 (Threshold: {threshold})")

            # Show analysis
            if "analysis" in result:
                print("\n📝 Detailed Analysis:")
                print("-" * 80)
                print(result["analysis"])
                print("-" * 80)

            # Check if result matches expectation
            expected_match = test_case["expected"] == "MATCH"
            if is_match == expected_match:
                print(f"\n✅ Test PASSED: Result matches expected ({test_case['expected']})")
            else:
                print(f"\n⚠️  Test FAILED: Expected {test_case['expected']}, got {'MATCH' if is_match else 'MISMATCH'}")

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
    print("🖊️" * 40)
    print("     SIGNATURE VERIFICATION API - TEST SUITE")
    print("🖊️" * 40)

    # Check server health
    print_header("Health Check")
    if not check_health():
        return

    # Run test cases
    for test_case in TEST_CASES:
        test_signature_verification(test_case)

    # Summary
    print_header("TEST SUMMARY")
    print("\n✅ All tests completed!")
    print(f"\n📊 Test Cases Run: {len(TEST_CASES)}")
    print("\n📝 Notes:")
    print("   • Genuine signatures should score 80+")
    print("   • Forged signatures should score below 80")
    print("   • Gemini model focuses on biometric writing traits")
    print()


if __name__ == '__main__':
    main()
