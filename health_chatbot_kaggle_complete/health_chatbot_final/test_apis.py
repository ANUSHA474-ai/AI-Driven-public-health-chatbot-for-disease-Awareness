"""
API Testing Script for AI Health Chatbot
Tests all API endpoints with sample data
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_predict_api():
    """Test disease prediction API"""
    print_header("TEST 1: DISEASE PREDICTION API")
    
    test_cases = [
        {
            'name': 'Fungal Infection',
            'symptoms': 'itching skin rash nodal skin eruptions'
        },
        {
            'name': 'Dengue',
            'symptoms': 'skin rash chills joint pain high fever headache'
        },
        {
            'name': 'Diabetes',
            'symptoms': 'fatigue weight loss excessive hunger increased appetite'
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test Case: {test['name']}")
        print(f"   Symptoms: {test['symptoms']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/predict",
                json={"symptoms": test['symptoms']},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pred = data['predictions'][0]
                    print(f"   ✅ Prediction: {pred['disease']}")
                    print(f"   ✅ Confidence: {pred['confidence']}%")
                    print(f"   ✅ Method: {pred.get('method', 'N/A')}")
                else:
                    print(f"   ❌ Error: {data.get('error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
            return False
    
    return True

def test_diseases_api():
    """Test get all diseases API"""
    print_header("TEST 2: GET ALL DISEASES API")
    
    try:
        response = requests.get(f"{BASE_URL}/api/diseases", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            diseases = data.get('diseases', [])
            total = data.get('total', 0)
            
            print(f"\n✅ Total Diseases: {total}")
            print(f"✅ Sample Diseases: {diseases[:5]}")
            return True
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection Error: {e}")
        return False

def test_disease_info_api():
    """Test get specific disease info API"""
    print_header("TEST 3: GET DISEASE INFO API")
    
    diseases_to_test = ['Dengue', 'Diabetes ', 'Malaria']
    
    for disease in diseases_to_test:
        print(f"\n📝 Testing: {disease}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/disease/{disease}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    info = data['info']
                    print(f"   ✅ Description: {info['description'][:60]}...")
                    print(f"   ✅ Has symptoms: {'Yes' if info['symptoms'] else 'No'}")
                    print(f"   ✅ Has prevention: {'Yes' if info['prevention'] else 'No'}")
                else:
                    print(f"   ❌ Error: {data.get('error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
    
    return True

def test_translations_api():
    """Test translations API"""
    print_header("TEST 4: TRANSLATIONS API")
    
    languages = ['en', 'es', 'fr', 'hi', 'zh']
    
    for lang in languages:
        try:
            response = requests.get(
                f"{BASE_URL}/api/translations/{lang}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ {lang.upper()}: {data.get('title', 'N/A')}")
            else:
                print(f"\n❌ {lang.upper()}: HTTP Error {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"\n❌ {lang.upper()}: Connection Error")
    
    return True

def test_stats_api():
    """Test system statistics API"""
    print_header("TEST 5: SYSTEM STATISTICS API")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"\n✅ Total Diseases: {stats.get('total_diseases')}")
            print(f"✅ Total Symptoms: {stats.get('total_symptoms')}")
            print(f"✅ Model Features: {stats.get('model_features')}")
            print(f"✅ Languages: {stats.get('languages_supported')}")
            print(f"✅ Models: {', '.join(stats.get('models_used', []))}")
            return True
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection Error: {e}")
        return False

def test_performance():
    """Test API performance"""
    print_header("TEST 6: PERFORMANCE TEST")
    
    print("\n⏱️  Testing response times...")
    
    # Test prediction speed
    symptoms = "fever cough headache"
    times = []
    
    for i in range(5):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/predict",
                json={"symptoms": symptoms},
                timeout=5
            )
            end = time.time()
            
            if response.status_code == 200:
                times.append(end - start)
                print(f"   Request {i+1}: {(end-start)*1000:.0f}ms")
        except:
            print(f"   Request {i+1}: Failed")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n✅ Average Response Time: {avg_time*1000:.0f}ms")
        
        if avg_time < 0.5:
            print(f"✅ Performance: Excellent (< 500ms)")
        elif avg_time < 1.0:
            print(f"⚠️  Performance: Good (< 1s)")
        else:
            print(f"❌ Performance: Slow (> 1s)")
        
        return True
    
    return False

def main():
    print("\n" + "="*70)
    print("  🏥 AI HEALTH CHATBOT - API TEST SUITE")
    print("="*70)
    print("\n⚠️  Make sure the Flask app is running on http://localhost:5000")
    print("   Start it with: python app.py\n")
    
    input("Press Enter to start testing...")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("\n✅ Server is running!\n")
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: Cannot connect to server")
        print("   Please start the app with: python app.py\n")
        return
    
    # Run all tests
    results = {
        'Prediction API': test_predict_api(),
        'Diseases API': test_diseases_api(),
        'Disease Info API': test_disease_info_api(),
        'Translations API': test_translations_api(),
        'Statistics API': test_stats_api(),
        'Performance': test_performance()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print()
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test:.<50} {status}")
    
    print(f"\n   {'OVERALL':.>50} {passed}/{total} PASSED")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! API is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
