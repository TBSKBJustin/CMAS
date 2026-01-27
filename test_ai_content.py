#!/usr/bin/env python3
"""
Test script for AI Content Processing module
"""

import sys
import requests
from pathlib import Path

def test_ollama_connection():
    """Test if Ollama service is available"""
    print("Testing Ollama connection...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running")
            print(f"  Installed models: {len(models)}")
            for model in models:
                print(f"    - {model.get('name')}")
            return True
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False

def test_recommended_model():
    """Check if recommended model is available"""
    print("\nChecking recommended model...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name') for m in models]
            
            recommended = 'qwen2.5:latest'
            if recommended in model_names:
                print(f"✓ Recommended model '{recommended}' is installed")
                return True
            else:
                print(f"✗ Recommended model '{recommended}' not found")
                print(f"  Install it with: ollama pull {recommended}")
                return False
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False

def test_ai_processor_import():
    """Test if AI processor module can be imported"""
    print("\nTesting AI processor module import...")
    try:
        from modules.content.ai_processor import AIContentProcessor
        print("✓ AIContentProcessor module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import AIContentProcessor: {e}")
        return False

def test_ai_processor_initialization():
    """Test AI processor initialization"""
    print("\nTesting AI processor initialization...")
    try:
        from modules.content.ai_processor import AIContentProcessor
        processor = AIContentProcessor(model="qwen2.5:latest")
        print("✓ AIContentProcessor initialized successfully")
        
        # Test Ollama availability check
        if processor._check_ollama_available():
            print("✓ Processor can connect to Ollama")
        else:
            print("✗ Processor cannot connect to Ollama")
            return False
        
        # Test model availability check
        if processor._check_model_available():
            print("✓ Model is available")
        else:
            print("✗ Model is not available")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to initialize processor: {e}")
        return False

def test_simple_prompt():
    """Test a simple prompt with Ollama"""
    print("\nTesting simple AI prompt...")
    try:
        from modules.content.ai_processor import AIContentProcessor
        processor = AIContentProcessor(model="qwen2.5:latest")
        
        test_prompt = "Say 'Hello, CMAS!' in a friendly way."
        print(f"  Sending test prompt: {test_prompt}")
        
        response = processor._call_ollama(test_prompt)
        
        if response:
            print(f"✓ AI responded: {response[:100]}...")
            return True
        else:
            print("✗ No response from AI")
            return False
    except Exception as e:
        print(f"✗ Failed to test prompt: {e}")
        return False

def test_subtitle_parsing():
    """Test SRT parsing"""
    print("\nTesting SRT parsing...")
    try:
        from modules.content.ai_processor import AIContentProcessor
        
        # Create test SRT content
        test_srt = """1
00:00:00,000 --> 00:00:05,000
Hello everyone

2
00:00:05,000 --> 00:00:10,000
This is a test subtitle
"""
        
        # Write test file
        test_file = Path("test_subtitle.srt")
        test_file.write_text(test_srt)
        
        processor = AIContentProcessor()
        subtitles = processor._parse_srt(str(test_file))
        
        test_file.unlink()  # Clean up
        
        if len(subtitles) == 2:
            print(f"✓ Successfully parsed {len(subtitles)} subtitle segments")
            return True
        else:
            print(f"✗ Expected 2 segments, got {len(subtitles)}")
            return False
    except Exception as e:
        print(f"✗ Failed to parse SRT: {e}")
        return False

def main():
    print("="*60)
    print("AI Content Processing Module - Test Suite")
    print("="*60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Ollama Connection", test_ollama_connection()))
    results.append(("Recommended Model", test_recommended_model()))
    results.append(("Module Import", test_ai_processor_import()))
    results.append(("Processor Initialization", test_ai_processor_initialization()))
    results.append(("Simple AI Prompt", test_simple_prompt()))
    results.append(("SRT Parsing", test_subtitle_parsing()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AI Content Processing is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
