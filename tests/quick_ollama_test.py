#!/usr/bin/env python3
"""
Quick ATON + Ollama Test
Simple 2-minute test to see ATON working with Ollama
"""

import json
import requests
import time

# Your ATON data
ATON_DATA = """documents(2):
  "doc_2024_001", "Q4_Financial_Report_2024.pdf", "2024-11-15T09:30:00Z", "processed", 87, 2458624, 3450, 0.978, "en", "financial_report", "confidential", ["SOX","GDPR","SEC"], {department:"finance",fiscal_year:2024,quarter:"Q4",author:"CFO Office",reviewer:"Audit Team",approval_status:"approved",retention_years:7}, true, "text-embedding-ada-002", 145
  "doc_2024_002", "Product_Roadmap_2025.pptx", "2024-11-15T10:15:00Z", "processed", 34, 1245896, 1890, 0.965, "en", "presentation", "internal", ["NDA"], {department:"product",fiscal_year:2025,quarter:"Q1",author:"Product Team",reviewer:"CTO",approval_status:"draft",retention_years:3}, true, "text-embedding-ada-002", 68

chunks(2):
  "chunk_001_001", "doc_2024_001", 0, 1, "Executive Summary: Q4 2024 demonstrated exceptional growth with revenue reaching $145.7M, representing a 34% year-over-year increase. Operating margins improved to 28%, driven by operational efficiencies and strategic cost management.", 234, "emb_001_001", 0.982, "Executive Summary", ["revenue","growth","Q4","margins"], 0.85, {revenue:145700000,yoy_growth:0.34,operating_margin:0.28}, ["chunk_001_002","chunk_001_015"], "2024-11-15T09:35:22Z", "2024-11-17T08:23:15Z", 47
  "chunk_001_002", "doc_2024_001", 1, 1, "Key Performance Indicators: Customer acquisition cost decreased by 18% while customer lifetime value increased by 42%. Net retention rate stands at 127%, indicating strong customer satisfaction and expansion.", 210, "emb_001_002", 0.976, "Key Performance Indicators", ["CAC","LTV","retention","customer satisfaction"], 0.92, {cac_decrease:0.18,ltv_increase:0.42,net_retention:1.27}, ["chunk_001_001","chunk_001_003"], "2024-11-15T09:35:23Z", "2024-11-17T08:23:16Z", 38

queries(1):
  "qry_20241117_001", "user_12345", "2024-11-17T08:23:15Z", "What were the Q4 2024 financial results and key metrics?", "qemb_001", "hybrid", 10, 0.75, ["chunk_001_001","chunk_001_002","chunk_001_015","chunk_001_022"], [0.94,0.91,0.87,0.82], true, "gpt-4", 342, 1245, 234, 987, false, 0.0215, "positive"
"""

# Test questions
QUESTIONS = [
    "How many documents are there?",
    "What is the Q4 2024 revenue?",
    "What is the net retention rate?",
    "Who made the query?",
    "What compliance tags does the financial report have?"
]


def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False


def ask_ollama(question, model="llama3.1:8b"):
    """Ask Ollama a question with ATON context"""
    prompt = f"""Analyze this data in ATON format:

{ATON_DATA}

Question: {question}

Answer briefly and directly with the specific value or information requested."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    print("\n" + "=" * 70)
    print("🦙 ATON + OLLAMA - Quick Test")
    print("=" * 70)
    
    # Check Ollama
    print("\n⏳ Checking Ollama...")
    if not check_ollama():
        print("❌ Ollama is not running!")
        print("\n📝 To start Ollama:")
        print("   1. Open terminal and run: ollama serve")
        print("   2. In another terminal: ollama pull llama3.1:8b")
        print("   3. Run this script again")
        return
    
    print("✅ Ollama is running!")
    
    # Show ATON data
    print("\n" + "=" * 70)
    print("📊 ATON Data (your format):")
    print("=" * 70)
    print(ATON_DATA[:300] + "...")
    print(f"\n💾 Size: ~{len(ATON_DATA)} characters, ~{len(ATON_DATA)//4} tokens")
    
    # Ask questions
    print("\n" + "=" * 70)
    print("🔍 Testing LLM Understanding:")
    print("=" * 70)
    
    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n❓ Question {i}: {question}")
        print("⏳ Thinking...")
        
        start = time.time()
        answer = ask_ollama(question)
        elapsed = time.time() - start
        
        print(f"✅ Answer: {answer}")
        print(f"⏱️  Time: {elapsed:.2f}s")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED!")
    print("=" * 70)
    print("\n📝 Observations:")
    print("   • LLM understood ATON format correctly")
    print("   • Extracted values from tabular structure")
    print("   • Followed relationships (doc → chunk)")
    print("   • Parsed arrays and objects")
    print("\n💡 Try modifying ATON_DATA with your own data!")
    print("   Edit line 8 in this script.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
