#!/usr/bin/env python3
"""
ATON + Ollama Test Suite
Comprehensive testing of ATON format with local LLM (Ollama)
"""

import json
import time
import sys
from pathlib import Path

# Add converter to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'converter'))

try:
    import requests
except ImportError:
    print("❌ requests not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

from aton import ATONEncoder


class OllamaATONTester:
    """Test ATON format with Ollama local LLM"""
    
    def __init__(self, model="llama3.1:8b", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.encoder = ATONEncoder(optimize=True)
        
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Ollama is running")
                print(f"📦 Available models: {[m['name'] for m in models]}")
                
                # Check if our model is available
                model_names = [m['name'] for m in models]
                if self.model not in model_names:
                    print(f"\n⚠️  Model '{self.model}' not found!")
                    print(f"💡 Run: ollama pull {self.model}")
                    return False
                return True
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Ollama is not running!")
            print("\n📝 To start Ollama:")
            print("   1. Install: https://ollama.ai")
            print("   2. Run: ollama serve")
            print(f"   3. Pull model: ollama pull {self.model}")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, stream=False):
        """Send query to Ollama"""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": 0.3,  # Lower for more consistent results
                    "top_p": 0.9
                }
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            if stream:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            full_response += data['response']
                            if not data.get('done', False):
                                print(data['response'], end='', flush=True)
                print()
                result = full_response
            else:
                result = response.json()['response']
            
            elapsed = time.time() - start_time
            
            return {
                'response': result,
                'elapsed_time': elapsed,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"Error: {str(e)}",
                'elapsed_time': 0,
                'success': False
            }
    
    def estimate_tokens(self, text):
        """Rough token estimation"""
        return len(text) // 4
    
    def test_rag_scenario(self):
        """Test 1: RAG Document Retrieval Scenario"""
        print("\n" + "=" * 80)
        print("TEST 1: RAG Document Retrieval (Real-World Scenario)")
        print("=" * 80)
        
        # Sample RAG data
        rag_data = {
            "documents": [
                {
                    "document_id": "doc_2024_001",
                    "filename": "Q4_Financial_Report_2024.pdf",
                    "upload_date": "2024-11-15T09:30:00Z",
                    "status": "processed",
                    "total_pages": 87,
                    "confidence_score": 0.978,
                    "language": "en",
                    "document_type": "financial_report",
                    "classification": "confidential"
                }
            ],
            "chunks": [
                {
                    "chunk_id": "chunk_001",
                    "document_id": "doc_2024_001",
                    "page": 1,
                    "content": "Executive Summary: Q4 2024 demonstrated exceptional growth with revenue reaching $145.7M, representing a 34% year-over-year increase. Operating margins improved to 28%, driven by operational efficiencies.",
                    "confidence": 0.982,
                    "entities": ["revenue", "growth", "Q4", "margins"]
                },
                {
                    "chunk_id": "chunk_002",
                    "document_id": "doc_2024_001",
                    "page": 2,
                    "content": "Key Performance Indicators: Customer acquisition cost decreased by 18% while customer lifetime value increased by 42%. Net retention rate stands at 127%.",
                    "confidence": 0.976,
                    "entities": ["CAC", "LTV", "retention"]
                }
            ]
        }
        
        # Convert to JSON and ATON
        json_str = json.dumps(rag_data, indent=2)
        aton_str = self.encoder.encode(rag_data)
        
        json_tokens = self.estimate_tokens(json_str)
        aton_tokens = self.estimate_tokens(aton_str)
        
        print(f"\n📊 Data Size Comparison:")
        print(f"   JSON: {json_tokens} tokens, {len(json_str)} bytes")
        print(f"   ATON: {aton_tokens} tokens, {len(aton_str)} bytes")
        print(f"   Reduction: {((json_tokens - aton_tokens) / json_tokens * 100):.1f}%")
        
        # Test question
        question = "What were the Q4 2024 financial results and key metrics?"
        
        # Test with JSON
        print(f"\n🔵 Testing with JSON format...")
        json_prompt = f"""Based on these documents in JSON format:

{json_str}

Question: {question}

Provide a concise answer with specific numbers."""
        
        json_result = self.query_ollama(json_prompt)
        
        # Test with ATON
        print(f"\n🟢 Testing with ATON format...")
        aton_prompt = f"""Based on these documents in ATON format:

{aton_str}

Question: {question}

Provide a concise answer with specific numbers."""
        
        aton_result = self.query_ollama(aton_prompt)
        
        # Compare results
        print("\n" + "=" * 80)
        print("RESULTS COMPARISON")
        print("=" * 80)
        
        print("\n📝 JSON Response:")
        print(f"   Time: {json_result['elapsed_time']:.2f}s")
        print(f"   Response: {json_result['response'][:200]}...")
        
        print("\n📝 ATON Response:")
        print(f"   Time: {aton_result['elapsed_time']:.2f}s")
        print(f"   Response: {aton_result['response'][:200]}...")
        
        if json_result['success'] and aton_result['success']:
            print("\n✅ Both formats processed successfully!")
            print(f"⚡ Speed improvement: {((json_result['elapsed_time'] - aton_result['elapsed_time']) / json_result['elapsed_time'] * 100):.1f}%")
        
        return {
            'json_tokens': json_tokens,
            'aton_tokens': aton_tokens,
            'json_time': json_result['elapsed_time'],
            'aton_time': aton_result['elapsed_time']
        }
    
    def test_data_extraction(self):
        """Test 2: Data Extraction Capabilities"""
        print("\n" + "=" * 80)
        print("TEST 2: Data Extraction & Understanding")
        print("=" * 80)
        
        # Your original ATON data
        aton_data = """documents(2):
  "doc_2024_001", "Q4_Financial_Report_2024.pdf", "2024-11-15T09:30:00Z", "processed", 87, 2458624, 3450, 0.978, "en", "financial_report", "confidential", ["SOX","GDPR","SEC"], {department:"finance",fiscal_year:2024,quarter:"Q4",author:"CFO Office",reviewer:"Audit Team",approval_status:"approved",retention_years:7}, true, "text-embedding-ada-002", 145
  "doc_2024_002", "Product_Roadmap_2025.pptx", "2024-11-15T10:15:00Z", "processed", 34, 1245896, 1890, 0.965, "en", "presentation", "internal", ["NDA"], {department:"product",fiscal_year:2025,quarter:"Q1",author:"Product Team",reviewer:"CTO",approval_status:"draft",retention_years:3}, true, "text-embedding-ada-002", 68

chunks(2):
  "chunk_001_001", "doc_2024_001", 0, 1, "Executive Summary: Q4 2024 demonstrated exceptional growth with revenue reaching $145.7M, representing a 34% year-over-year increase. Operating margins improved to 28%, driven by operational efficiencies and strategic cost management.", 234, "emb_001_001", 0.982, "Executive Summary", ["revenue","growth","Q4","margins"], 0.85, {revenue:145700000,yoy_growth:0.34,operating_margin:0.28}, ["chunk_001_002","chunk_001_015"], "2024-11-15T09:35:22Z", "2024-11-17T08:23:15Z", 47
  "chunk_001_002", "doc_2024_001", 1, 1, "Key Performance Indicators: Customer acquisition cost decreased by 18% while customer lifetime value increased by 42%. Net retention rate stands at 127%, indicating strong customer satisfaction and expansion.", 210, "emb_001_002", 0.976, "Key Performance Indicators", ["CAC","LTV","retention","customer satisfaction"], 0.92, {cac_decrease:0.18,ltv_increase:0.42,net_retention:1.27}, ["chunk_001_001","chunk_001_003"], "2024-11-15T09:35:23Z", "2024-11-17T08:23:16Z", 38

queries(1):
  "qry_20241117_001", "user_12345", "2024-11-17T08:23:15Z", "What were the Q4 2024 financial results and key metrics?", "qemb_001", "hybrid", 10, 0.75, ["chunk_001_001","chunk_001_002","chunk_001_015","chunk_001_022"], [0.94,0.91,0.87,0.82], true, "gpt-4", 342, 1245, 234, 987, false, 0.0215, "positive"
"""
        
        questions = [
            "How many documents are in the system?",
            "What is the revenue mentioned in Q4 2024?",
            "What is the net retention rate?",
            "Who made the query and when?",
            "What compliance tags does the financial report have?"
        ]
        
        print(f"\n📊 ATON Data ({self.estimate_tokens(aton_data)} tokens):")
        print(aton_data[:300] + "...\n")
        
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Question {i}: {question}")
            
            prompt = f"""Analyze this data in ATON format:

{aton_data}

Question: {question}

Provide a brief, direct answer with the specific value."""
            
            result = self.query_ollama(prompt)
            
            if result['success']:
                print(f"✅ Answer: {result['response']}")
                print(f"⏱️  Time: {result['elapsed_time']:.2f}s")
            else:
                print(f"❌ Error: {result['response']}")
    
    def test_comparison(self):
        """Test 3: Side-by-Side Format Comparison"""
        print("\n" + "=" * 80)
        print("TEST 3: Format Comparison - Comprehension Test")
        print("=" * 80)
        
        # Simple product data
        products = {
            "products": [
                {"id": 1, "name": "Laptop Pro 15", "price": 2199.00, "stock": 47, "rating": 4.7},
                {"id": 2, "name": "Wireless Mouse", "price": 79.00, "stock": 156, "rating": 4.5},
                {"id": 3, "name": "USB-C Hub", "price": 49.00, "stock": 89, "rating": 4.3}
            ]
        }
        
        json_str = json.dumps(products, indent=2)
        aton_str = self.encoder.encode(products)
        
        print(f"\n📊 JSON ({self.estimate_tokens(json_str)} tokens):")
        print(json_str)
        
        print(f"\n📊 ATON ({self.estimate_tokens(aton_str)} tokens):")
        print(aton_str)
        
        questions = [
            "What is the most expensive product?",
            "How many products have stock > 100?",
            "What is the average rating?"
        ]
        
        for question in questions:
            print(f"\n{'─' * 80}")
            print(f"❓ {question}")
            print(f"{'─' * 80}")
            
            # Test JSON
            print("\n🔵 JSON Response:")
            json_prompt = f"Data: {json_str}\n\nQuestion: {question}\nAnswer briefly:"
            json_result = self.query_ollama(json_prompt)
            if json_result['success']:
                print(f"   {json_result['response']}")
                print(f"   ⏱️  {json_result['elapsed_time']:.2f}s")
            
            # Test ATON
            print("\n🟢 ATON Response:")
            aton_prompt = f"Data: {aton_str}\n\nQuestion: {question}\nAnswer briefly:"
            aton_result = self.query_ollama(aton_prompt)
            if aton_result['success']:
                print(f"   {aton_result['response']}")
                print(f"   ⏱️  {aton_result['elapsed_time']:.2f}s")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "=" * 80)
        print("ATON + OLLAMA TEST SUITE")
        print("=" * 80)
        print(f"Model: {self.model}")
        print(f"Ollama URL: {self.ollama_url}")
        
        # Check Ollama
        if not self.check_ollama():
            return
        
        print("\n⏳ Starting tests... (this may take a few minutes)\n")
        
        # Run tests
        try:
            test1_results = self.test_rag_scenario()
            self.test_data_extraction()
            self.test_comparison()
            
            # Final summary
            print("\n" + "=" * 80)
            print("FINAL SUMMARY")
            print("=" * 80)
            
            if test1_results:
                token_savings = ((test1_results['json_tokens'] - test1_results['aton_tokens']) / 
                               test1_results['json_tokens'] * 100)
                
                print(f"\n📊 Token Efficiency:")
                print(f"   JSON: {test1_results['json_tokens']} tokens")
                print(f"   ATON: {test1_results['aton_tokens']} tokens")
                print(f"   Savings: {token_savings:.1f}%")
                
                print(f"\n⚡ Performance:")
                print(f"   JSON time: {test1_results['json_time']:.2f}s")
                print(f"   ATON time: {test1_results['aton_time']:.2f}s")
                
                if test1_results['aton_time'] < test1_results['json_time']:
                    speed_improvement = ((test1_results['json_time'] - test1_results['aton_time']) / 
                                       test1_results['json_time'] * 100)
                    print(f"   Speed improvement: {speed_improvement:.1f}%")
            
            print("\n✅ All tests completed!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during tests: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ATON format with Ollama')
    parser.add_argument('--model', default='llama3.1:8b', 
                       help='Ollama model to use (default: llama3.1:8b)')
    parser.add_argument('--url', default='http://localhost:11434',
                       help='Ollama API URL (default: http://localhost:11434)')
    parser.add_argument('--test', choices=['rag', 'extract', 'compare', 'all'],
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    tester = OllamaATONTester(model=args.model, ollama_url=args.url)
    
    if args.test == 'all':
        tester.run_all_tests()
    elif args.test == 'rag':
        tester.test_rag_scenario()
    elif args.test == 'extract':
        tester.test_data_extraction()
    elif args.test == 'compare':
        tester.test_comparison()


if __name__ == "__main__":
    main()
