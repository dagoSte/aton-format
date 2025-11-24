# 🧪 ATON Testing Suite

Test completi per validare ATON con LLM locali e cloud.

## 📁 File in questa Directory

```
tests/
├── test_ollama.py          # Test completo con Ollama (3 scenari)
├── quick_ollama_test.py    # Test rapido 2 minuti
├── OLLAMA_TEST_GUIDE.md    # Guida dettagliata Ollama
└── README.md               # Questo file
```

## 🚀 Quick Start

### Opzione 1: Test Rapido (2 minuti)

```bash
# 1. Avvia Ollama
ollama serve

# 2. (Altro terminale) Scarica modello
ollama pull llama3.1:8b

# 3. Test rapido
python3 quick_ollama_test.py
```

**Output:**
```
🦙 ATON + OLLAMA - Quick Test
======================================================================
✅ Ollama is running!

📊 ATON Data (your format):
documents(2):
  "doc_2024_001", ...
...

🔍 Testing LLM Understanding:
======================================================================

❓ Question 1: How many documents are there?
✅ Answer: There are 2 documents
⏱️  Time: 1.23s

❓ Question 2: What is the Q4 2024 revenue?
✅ Answer: $145.7M
⏱️  Time: 1.45s

...

✅ TEST COMPLETED!
```

### Opzione 2: Test Completo (15 minuti)

```bash
# Test tutti gli scenari
python3 test_ollama.py

# O test specifici
python3 test_ollama.py --test rag      # Solo RAG scenario
python3 test_ollama.py --test extract  # Solo extraction
python3 test_ollama.py --test compare  # Solo comparison
```

## 📊 Cosa Testano gli Script

### `quick_ollama_test.py` - Test Rapido

**5 Domande sui TUOI dati ATON:**

```python
ATON_DATA = """
documents(2):
  "doc_2024_001", "Q4_Financial_Report_2024.pdf", ...
chunks(2):
  "chunk_001_001", "doc_2024_001", ...
queries(1):
  "qry_20241117_001", "user_12345", ...
"""

QUESTIONS = [
    "How many documents are there?",
    "What is the Q4 2024 revenue?",
    "What is the net retention rate?",
    "Who made the query?",
    "What compliance tags does the financial report have?"
]
```

**Verifica:**
- ✅ LLM capisce ATON format
- ✅ Estrae valori correttamente
- ✅ Legge arrays `["SOX","GDPR"]`
- ✅ Legge objects `{revenue:145700000}`
- ✅ Segue relationships

### `test_ollama.py` - Test Completo

**3 Scenari Completi:**

#### Test 1: RAG System
- Documenti + chunks con metadata
- Query utente reale
- **Confronta JSON vs ATON:**
  - Token count
  - Response time
  - Answer quality

#### Test 2: Data Extraction
- Usa i tuoi dati ATON
- 5 domande specifiche
- **Verifica accuracy:**
  - Valori numerici
  - Date e timestamp
  - Arrays e objects
  - Relationships

#### Test 3: Format Comparison
- Stesso dataset in JSON e ATON
- 3 domande identiche
- **Side-by-side:**
  - Response quality
  - Speed
  - Token usage

## 🎯 Risultati Attesi

### Token Reduction

```
JSON:  ████████████████████████████ (720 tokens)
ATON:  ████████████ (310 tokens)
       ↓↓↓ 57% REDUCTION ↓↓↓
```

### Performance

| Metrica | JSON | ATON | Improvement |
|---------|------|------|-------------|
| Tokens | 720 | 310 | **-57%** |
| Time | 3.4s | 2.2s | **-35%** |
| Accuracy | 95% | 94% | -1% |

### LLM Comprehension

```
✅ Capisce struttura tabellare
✅ Estrae valori specifici
✅ Interpreta arrays []
✅ Interpreta objects {}
✅ Segue relationships ->
✅ Mantiene accuracy ~95%
```

## 🔧 Personalizzazione

### Usa i Tuoi Dati

**Quick Test:**
```python
# Modifica quick_ollama_test.py linea 8:
ATON_DATA = """
# I TUOI DATI ATON QUI
products(100):
  1, "Product A", 99.00, ...
  ...
"""

# Linea 18 - Le tue domande:
QUESTIONS = [
    "Quanti prodotti ci sono?",
    "Qual è il più costoso?",
    ...
]
```

**Test Completo:**
```python
# Modifica test_ollama.py metodo test_data_extraction():
aton_data = """
# I TUOI DATI ATON
"""

questions = [
    "La tua domanda 1",
    "La tua domanda 2",
    ...
]
```

### Cambia Modello

```bash
# Modelli disponibili
ollama list

# Usa modello diverso
python3 test_ollama.py --model mistral:7b
python3 test_ollama.py --model llama3.2:3b

# Quick test (modifica linea 88):
def ask_ollama(question, model="mistral:7b"):
```

### Ollama Remoto

```bash
# Se Ollama è su altro server
python3 test_ollama.py --url http://192.168.1.100:11434
```

## 📋 Prerequisiti

### Software Necessario

```bash
# 1. Python 3.8+
python3 --version

# 2. Ollama
ollama --version

# 3. requests library
pip install requests
```

### Modelli Raccomandati

| Modello | Dimensione | RAM | Velocità | Accuracy |
|---------|-----------|-----|----------|----------|
| **llama3.2:3b** | 2GB | 4GB | ⚡⚡⚡ | ⭐⭐⭐ |
| **llama3.1:8b** | 4.7GB | 8GB | ⚡⚡ | ⭐⭐⭐⭐ |
| **mistral:7b** | 4.1GB | 8GB | ⚡⚡ | ⭐⭐⭐⭐ |
| **llama3.1:70b** | 40GB | 64GB | ⚡ | ⭐⭐⭐⭐⭐ |

### Download Modelli

```bash
# Raccomandato per testing
ollama pull llama3.1:8b

# Più veloce (laptop)
ollama pull llama3.2:3b

# Più accurato (server)
ollama pull llama3.1:70b
```

## 🐛 Troubleshooting

### Ollama non parte

```bash
# Verifica processo
ps aux | grep ollama

# Porta già in uso?
lsof -i :11434

# Riavvia
pkill ollama
ollama serve
```

### Modello non trovato

```bash
# Lista modelli installati
ollama list

# Scarica se mancante
ollama pull llama3.1:8b

# Verifica download
ls ~/.ollama/models/
```

### Test troppo lenti

```bash
# 1. Usa modello più piccolo
python3 test_ollama.py --model llama3.2:3b

# 2. Solo quick test
python3 quick_ollama_test.py

# 3. Test singolo
python3 test_ollama.py --test rag
```

### Out of Memory

```bash
# Usa modello più piccolo
ollama pull phi3:mini  # Solo 2.3GB
python3 test_ollama.py --model phi3:mini

# O aumenta swap
sudo swapon --show
```

### Timeout errors

```python
# Aumenta timeout nel codice
# test_ollama.py linea ~70:
timeout=180  # invece di 60
```

## 📊 Interpretare i Risultati

### Good Results ✅

```
Token Reduction: 55-60% ✅
Speed Improvement: 30-40% ✅
Accuracy Maintained: 93%+ ✅
All Questions Answered ✅
No Parsing Errors ✅
```

### Expected Results

```
Token Reduction: 50-60% (normale)
Speed Improvement: 25-45% (varia per modello)
Accuracy: 90-96% (entrambi formati)
Some minor differences in wording (OK)
```

### Issues to Investigate

```
Token Reduction: <40% ⚠️
  → Check ATON optimization
  
Speed Degradation ⚠️
  → Model too large?
  → Cold start?
  
Accuracy Drop: >5% ⚠️
  → Check prompt quality
  → Try different model
  
Parsing Errors ❌
  → Check ATON syntax
  → Validate data
```

## 🎓 Tips & Best Practices

### 1. Warm-up il Modello

```bash
# Prima del benchmark
ollama run llama3.1:8b "test" > /dev/null
```

### 2. Più Test per Accuracy

```bash
# Esegui 3 volte, fai media
for i in {1..3}; do
  python3 quick_ollama_test.py | tee -a results.txt
done
```

### 3. Log Dettagliati

```bash
# Salva output completo
python3 test_ollama.py 2>&1 | tee test_$(date +%Y%m%d_%H%M%S).log
```

### 4. Confronta Modelli

```bash
# Test con diversi modelli
for model in llama3.2:3b llama3.1:8b mistral:7b; do
  echo "Testing $model..."
  python3 test_ollama.py --model $model --test rag
done
```

### 5. Benchmark Sistematico

```python
# Script per benchmark multipli
models = ["llama3.2:3b", "llama3.1:8b", "mistral:7b"]
tests = ["rag", "extract", "compare"]

for model in models:
    for test in tests:
        run_test(model, test)
        save_results()
```

## 📈 Next Steps

### Dopo i Test di Base

1. **Valida Risultati**
   - Token savings verificati?
   - Accuracy accettabile?
   - Speed improvement reale?

2. **Test con Dati Reali**
   - Usa i tuoi dataset
   - Test su production data
   - Measure real-world impact

3. **Scale Testing**
   - Test con dataset grandi
   - Multiple concurrent requests
   - Long-running sessions

4. **Integration Testing**
   - Integra in pipeline RAG
   - Test end-to-end
   - Production deployment

### Contribuisci

- Report your results
- Share benchmarks
- Suggest improvements
- Report issues

## 📞 Help & Resources

### Documentazione

- **Ollama Guide**: `OLLAMA_TEST_GUIDE.md`
- **ATON Spec**: `../docs/WHITEPAPER.md`
- **Examples**: `../examples/ADVANCED_EXAMPLES.md`

### External Links

- Ollama: https://ollama.ai
- Models: https://ollama.ai/library
- API Docs: https://github.com/ollama/ollama/blob/main/docs/api.md

### Quick Commands

```bash
# Ollama status
ollama list
curl http://localhost:11434/api/tags

# Quick test
python3 quick_ollama_test.py

# Full test
python3 test_ollama.py

# Specific test
python3 test_ollama.py --test rag --model llama3.2:3b

# Help
python3 test_ollama.py --help
```

---

## 🎉 Ready to Test!

**3 Comandi per Iniziare:**

```bash
# Terminal 1
ollama serve

# Terminal 2
ollama pull llama3.1:8b

# Terminal 3
python3 quick_ollama_test.py
```

**Vedrai l'LLM comprendere ATON in tempo reale! 🚀**
