"""
Test script to verify Google AI Studio API key is working
Run this to test your API key: python -m app.services.test_ai
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

load_dotenv()

def test_api_key():
    """Test if the Google AI Studio API key is configured and working"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY not found in environment variables")
        print("\nTo fix this:")
        print("1. Create a .env file in the backend/ directory")
        print("2. Add: GOOGLE_AI_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✓ Found API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try to create a model instance
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
            except:
                model = genai.GenerativeModel('gemini-pro')
        
        # Make a test API call
        print("Testing API call...")
        response = model.generate_content("Say 'Hello, API is working!' if you can read this.")
        
        if hasattr(response, 'text'):
            print(f"✓ API Response: {response.text[:100]}")
        else:
            print(f"✓ API Response received: {str(response)[:100]}")
        
        print("\n✅ SUCCESS: Google AI Studio API key is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to use API key")
        print(f"   Error: {e}")
        print("\nPossible issues:")
        print("1. API key is invalid or expired")
        print("2. API quota has been exceeded")
        print("3. Network connectivity issues")
        print("4. Google AI Studio service is down")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google AI Studio API Key Test")
    print("=" * 60)
    print()
    test_api_key()
