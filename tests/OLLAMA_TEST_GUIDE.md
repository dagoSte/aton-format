# 🦙 ATON + Ollama Test Guide

## Quick Start (5 minuti)

### Step 1: Installa Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Scarica da: https://ollama.ai/download/windows

# Verifica installazione
ollama --version
```

### Step 2: Scarica un Modello

```bash
# Modello raccomandato (4.7GB)
ollama pull llama3.1:8b

# Alternative più leggere:
ollama pull llama3.2:3b     # 2GB - più veloce
ollama pull phi3:mini       # 2.3GB - Microsoft

# Alternative più potenti:
ollama pull llama3.1:70b    # 40GB - molto accurato
ollama pull mistral:7b      # 4.1GB - ottimo balance
```

### Step 3: Avvia Ollama

```bash
# Terminale 1: Avvia server
ollama serve

# Terminale 2: Test veloce
ollama run llama3.1:8b "Hello, how are you?"
```

### Step 4: Esegui Test ATON

```bash
# Vai alla directory del progetto
cd aton-project

# Esegui test completo
python3 tests/test_ollama.py

# O test specifico
python3 tests/test_ollama.py --test rag      # Solo RAG
python3 tests/test_ollama.py --test extract  # Solo extraction
python3 tests/test_ollama.py --test compare  # Solo comparison
```

---

## 🎯 Cosa Testa lo Script

### Test 1: RAG Document Retrieval ⭐⭐⭐⭐⭐

**Scenario Real-World:**
- 2 documenti (Financial Report + Product Roadmap)
- 2 chunks con contenuto finanziario
- Query utente: "What were the Q4 2024 financial results?"

**Confronta:**
```
JSON Format (720 tokens):
{
  "documents": [...],
  "chunks": [...]
}

vs

ATON Format (310 tokens):
documents(2):
  "doc_001", "Q4_Report.pdf", ...
chunks(2):
  "chunk_001", "doc_001", ...
```

**Verifica:**
- ✅ LLM comprende entrambi i formati?
- ✅ ATON risparmia davvero 57% tokens?
- ✅ Risposte hanno stessa qualità?
- ✅ ATON è più veloce?

### Test 2: Data Extraction ⭐⭐⭐⭐⭐

**Usa i TUOI dati ATON:**
```aton
documents(2):
  "doc_2024_001", "Q4_Financial_Report_2024.pdf", ...
chunks(2):
  "chunk_001_001", "doc_2024_001", ...
queries(1):
  "qry_20241117_001", "user_12345", ...
```

**5 Domande Specifiche:**
1. "How many documents are in the system?"
2. "What is the revenue mentioned in Q4 2024?"
3. "What is the net retention rate?"
4. "Who made the query and when?"
5. "What compliance tags does the financial report have?"

**Verifica:**
- ✅ LLM estrae valori corretti?
- ✅ Comprende struttura tabellare?
- ✅ Segue relationships (doc → chunk)?
- ✅ Legge nested objects {revenue:145700000}?
- ✅ Interpreta arrays ["SOX","GDPR","SEC"]?

### Test 3: Format Comparison ⭐⭐⭐⭐⭐

**Stesso Dataset, 2 Formati:**
```
Prodotti: Laptop, Mouse, USB Hub
Con: ID, Name, Price, Stock, Rating
```

**3 Domande:**
1. "What is the most expensive product?"
2. "How many products have stock > 100?"
3. "What is the average rating?"

**Confronta Side-by-Side:**
- JSON response vs ATON response
- Token count: JSON vs ATON
- Response time: JSON vs ATON
- Accuracy: entrambi corretti?

---

## 📊 Output Atteso

### Esempio Output Test 1 (RAG)

```
================================================================================
TEST 1: RAG Document Retrieval (Real-World Scenario)
================================================================================

📊 Data Size Comparison:
   JSON: 720 tokens, 2880 bytes
   ATON: 310 tokens, 1240 bytes
   Reduction: 56.9%

🔵 Testing with JSON format...
⏳ Generating response...

🟢 Testing with ATON format...
⏳ Generating response...

================================================================================
RESULTS COMPARISON
================================================================================

📝 JSON Response:
   Time: 3.42s
   Response: Based on the financial documents, Q4 2024 showed exceptional 
   performance with revenue of $145.7M, representing a 34% year-over-year 
   increase. Operating margins improved to 28%...

📝 ATON Response:
   Time: 2.18s
   Response: Q4 2024 results: Revenue reached $145.7M (+34% YoY), operating 
   margins improved to 28%, CAC decreased by 18%, LTV increased by 42%, and 
   net retention stands at 127%...

✅ Both formats processed successfully!
⚡ Speed improvement: 36.3%
```

### Esempio Output Test 2 (Extraction)

```
================================================================================
TEST 2: Data Extraction & Understanding
================================================================================

📊 ATON Data (892 tokens):
documents(2):
  "doc_2024_001", "Q4_Financial_Report_2024.pdf", ...
...

❓ Question 1: How many documents are in the system?
✅ Answer: There are 2 documents in the system
⏱️  Time: 1.23s

❓ Question 2: What is the revenue mentioned in Q4 2024?
✅ Answer: The revenue reached $145.7M in Q4 2024
⏱️  Time: 1.45s

❓ Question 3: What is the net retention rate?
✅ Answer: The net retention rate is 127%
⏱️  Time: 1.18s

❓ Question 4: Who made the query and when?
✅ Answer: User user_12345 made the query on 2024-11-17 at 08:23:15Z
⏱️  Time: 1.56s

❓ Question 5: What compliance tags does the financial report have?
✅ Answer: The compliance tags are: SOX, GDPR, and SEC
⏱️  Time: 1.34s
```

### Esempio Output Test 3 (Comparison)

```
================================================================================
TEST 3: Format Comparison - Comprehension Test
================================================================================

📊 JSON (125 tokens):
{
  "products": [
    {"id": 1, "name": "Laptop Pro 15", "price": 2199.00, "stock": 47},
    ...
  ]
}

📊 ATON (55 tokens):
@schema[id:int, name:str, price:float, stock:int, rating:float]
products(3):
  1, "Laptop Pro 15", 2199.00, 47, 4.7
  2, "Wireless Mouse", 79.00, 156, 4.5
  3, "USB-C Hub", 49.00, 89, 4.3

────────────────────────────────────────────────────────────────────────────────
❓ What is the most expensive product?

🔵 JSON Response:
   The most expensive product is Laptop Pro 15 at $2199.00
   ⏱️  2.34s

🟢 ATON Response:
   The most expensive product is Laptop Pro 15 priced at $2199.00
   ⏱️  1.67s

────────────────────────────────────────────────────────────────────────────────
❓ How many products have stock > 100?

🔵 JSON Response:
   One product has stock greater than 100: Wireless Mouse with 156 units
   ⏱️  2.51s

🟢 ATON Response:
   1 product has stock > 100 (Wireless Mouse: 156)
   ⏱️  1.89s
```

### Final Summary

```
================================================================================
FINAL SUMMARY
================================================================================

📊 Token Efficiency:
   JSON: 720 tokens
   ATON: 310 tokens
   Savings: 56.9%

⚡ Performance:
   JSON time: 3.42s
   ATON time: 2.18s
   Speed improvement: 36.3%

✅ All tests completed!
```

---

## 🎨 Personalizza i Test

### Usa i Tuoi Dati

Modifica `tests/test_ollama.py`:

```python
# Linea ~180 - Test 2
aton_data = """
# I TUOI DATI ATON QUI
documents(5):
  ...
chunks(100):
  ...
"""

# Linea ~215 - Le tue domande
questions = [
    "La tua domanda 1?",
    "La tua domanda 2?",
    ...
]
```

### Cambia Modello

```bash
# Usa modello diverso
python3 tests/test_ollama.py --model llama3.2:3b

# Ollama su server remoto
python3 tests/test_ollama.py --url http://192.168.1.100:11434
```

### Test Singolo

```bash
# Solo RAG (veloce)
python3 tests/test_ollama.py --test rag

# Solo estrazione dati
python3 tests/test_ollama.py --test extract

# Solo confronto formati
python3 tests/test_ollama.py --test compare
```

---

## 🔧 Troubleshooting

### Errore: "Ollama is not running"

```bash
# Terminal 1: Avvia Ollama
ollama serve

# Terminal 2: Verifica
curl http://localhost:11434/api/tags
```

### Errore: "Model not found"

```bash
# Lista modelli installati
ollama list

# Scarica il modello
ollama pull llama3.1:8b
```

### Errore: "Connection timeout"

```bash
# Aumenta timeout nel codice
# Oppure usa modello più piccolo
ollama pull llama3.2:3b
python3 tests/test_ollama.py --model llama3.2:3b
```

### Errore: "Out of memory"

```bash
# Usa modello più piccolo
ollama pull phi3:mini  # Solo 2.3GB

# O limita context
# Nel codice, riduci la dimensione dei dati test
```

### Test troppo lenti?

```bash
# Usa modello più veloce
python3 tests/test_ollama.py --model llama3.2:3b

# O test singolo invece di --test all
python3 tests/test_ollama.py --test rag
```

---

## 📈 Benchmark Attesi

### Performance per Modello

| Modello | Token/sec | Accuratezza | RAM |
|---------|-----------|-------------|-----|
| llama3.2:3b | ~50-80 | 85-90% | 4GB |
| llama3.1:8b | ~30-50 | 90-95% | 8GB |
| mistral:7b | ~35-55 | 88-93% | 8GB |
| llama3.1:70b | ~8-15 | 95-98% | 40GB |

### ATON vs JSON - Risultati Tipici

| Metrica | JSON | ATON | Miglioramento |
|---------|------|------|---------------|
| **Token Count** | 100% | 44% | -56% |
| **Processing Time** | 100% | 65% | -35% |
| **Accuracy** | 95% | 94% | -1% |
| **Cost** | 100% | 44% | -56% |

---

## 💡 Tips per Best Results

### 1. Warm-up del Modello

```bash
# Prima del test, fai warm-up
ollama run llama3.1:8b "Test" > /dev/null
```

### 2. Usa Temperature Bassa

```python
# Nel codice, temperature già settata a 0.3
# Per risultati ancora più deterministici:
"temperature": 0.1
```

### 3. Test Multipli

```bash
# Esegui 3 volte e fai media
for i in {1..3}; do
  python3 tests/test_ollama.py --test rag
done
```

### 4. Logging Dettagliato

```python
# Aggiungi nel codice per debug:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎯 Cosa Aspettarsi

### ✅ Success Indicators

- LLM risponde correttamente a tutte le domande
- ATON usa ~56% meno token di JSON
- ATON è ~30-40% più veloce
- Accuracy simile (±2%)
- Nessun errore di parsing

### ⚠️ Known Limitations

- Modelli piccoli (<7B) possono avere accuracy leggermente inferiore
- Prima risposta può essere più lenta (cold start)
- Nested objects complessi potrebbero richiedere prompt tuning
- Molto dipende dal contesto e dalla complessità query

### 🎖️ Best Case Scenario

```
✅ Token reduction: 55-60%
✅ Speed improvement: 35-45%
✅ Accuracy maintained: 95%+
✅ All tests pass
✅ LLM comprende ATON perfettamente
```

---

## 🚀 Prossimi Passi

### Dopo i Test

1. **Analizza Results**
   - Confronta accuratezza
   - Misura savings
   - Verifica comprensione

2. **Integra in Produzione**
   - Usa ATON per RAG pipeline
   - Implementa in API
   - Monitor performance

3. **Benchmark Estesi**
   - Test con più modelli
   - Dataset più grandi
   - Casi edge

4. **Contribuisci**
   - Condividi risultati
   - Report issues
   - Suggerisci improvements

---

## 📞 Help & Support

### Quick Commands

```bash
# Check Ollama
ollama list

# Test singolo veloce
python3 tests/test_ollama.py --test rag --model llama3.2:3b

# Debug mode
python3 -u tests/test_ollama.py 2>&1 | tee test.log

# Stop Ollama
pkill ollama
```

### Documentazione

- Ollama: https://ollama.ai/docs
- Examples: `examples/ADVANCED_EXAMPLES.md`

---

**Ready to test? Let's go! 🦙🚀**

```bash
ollama serve
# In altro terminale:
python3 tests/test_ollama.py
```
