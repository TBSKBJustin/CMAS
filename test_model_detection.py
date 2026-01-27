#!/usr/bin/env python3
"""
Test script for dynamic model detection
"""

import sys
import requests
from pathlib import Path

API_BASE = "http://localhost:5001/api"

def test_whisper_models():
    """Test Whisper model detection"""
    print("Testing Whisper model detection...")
    try:
        response = requests.get(f"{API_BASE}/models/whisper", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            default = data.get('default')
            
            print(f"✓ Whisper API responded")
            print(f"  Found {len(models)} model(s):")
            for model in models:
                size_mb = model.get('size', 0) / (1024 * 1024)
                print(f"    - {model['value']} ({size_mb:.1f} MB)")
            print(f"  Default model: {default}")
            
            if len(models) > 0:
                print("✓ Whisper models available")
                return True
            else:
                print("⚠️  No Whisper models found")
                print("   Download models to: ../whisper.cpp/models/")
                print("   Example: download ggml-base.bin")
                return False
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("  Make sure API server is running: python api_server.py")
        return False

def test_ollama_models():
    """Test Ollama model detection"""
    print("\nTesting Ollama model detection...")
    try:
        response = requests.get(f"{API_BASE}/models/ollama", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            default = data.get('default')
            service_available = data.get('service_available')
            
            print(f"✓ Ollama API responded")
            print(f"  Service available: {service_available}")
            
            if service_available:
                print(f"  Found {len(models)} model(s):")
                for model in models:
                    size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
                    print(f"    - {model['value']} ({size_gb:.1f} GB)")
                print(f"  Default model: {default}")
                
                if len(models) > 0:
                    print("✓ Ollama models available")
                    return True
                else:
                    print("⚠️  No Ollama models found")
                    print("   Download a model: ollama pull qwen2.5:latest")
                    return False
            else:
                error = data.get('error', 'Unknown error')
                print(f"✗ Ollama service not available: {error}")
                print("  Start Ollama: ollama serve &")
                return False
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("  Make sure API server is running: python api_server.py")
        return False

def test_frontend_integration():
    """Test that frontend can access the APIs"""
    print("\nTesting frontend integration...")
    
    # Check if frontend API file exists
    api_file = Path("frontend/src/api.js")
    if not api_file.exists():
        print("✗ Frontend API file not found")
        return False
    
    # Check if API functions are defined
    content = api_file.read_text()
    
    checks = [
        ('getWhisperModels', 'get Whisper models function'),
        ('getOllamaModels', 'get Ollama models function'),
        ('/models/whisper', 'Whisper endpoint'),
        ('/models/ollama', 'Ollama endpoint'),
    ]
    
    all_found = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ Found {description}")
        else:
            print(f"✗ Missing {description}")
            all_found = False
    
    return all_found

def test_event_create_page():
    """Check if EventCreate page uses dynamic models"""
    print("\nTesting EventCreate page integration...")
    
    page_file = Path("frontend/src/pages/EventCreate.jsx")
    if not page_file.exists():
        print("✗ EventCreate.jsx not found")
        return False
    
    content = page_file.read_text()
    
    checks = [
        ('getWhisperModels', 'Whisper models query'),
        ('getOllamaModels', 'Ollama models query'),
        ('whisperModelsData', 'Whisper data binding'),
        ('ollamaModelsData', 'Ollama data binding'),
        ('whisperModelsData.models.map', 'Dynamic Whisper options'),
        ('ollamaModelsData.models.map', 'Dynamic Ollama options'),
    ]
    
    all_found = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ Found {description}")
        else:
            print(f"✗ Missing {description}")
            all_found = False
    
    return all_found

def main():
    print("="*60)
    print("Dynamic Model Detection - Test Suite")
    print("="*60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Whisper Models API", test_whisper_models()))
    results.append(("Ollama Models API", test_ollama_models()))
    results.append(("Frontend API Integration", test_frontend_integration()))
    results.append(("EventCreate Page Integration", test_event_create_page()))
    
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
        print("\n🎉 All tests passed! Dynamic model detection is working.")
        print("\nNext steps:")
        print("1. Start API server: python api_server.py")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Create a new event and see dynamic model lists")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
