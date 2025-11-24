# ATON Examples Collection

## Example 1: Simple E-commerce Product Catalog

### JSON Format
```json
{
  "products": [
    {
      "id": 1,
      "name": "Laptop",
      "price": 3999.90,
      "category": "Electronics",
      "in_stock": true
    },
    {
      "id": 2,
      "name": "Mouse",
      "price": 149.90,
      "category": "Accessories",
      "in_stock": true
    },
    {
      "id": 3,
      "name": "Headset",
      "price": 499.00,
      "category": "Audio",
      "in_stock": false
    }
  ]
}
```

**Tokens: ~125**

### ATON Format
```aton
@schema[id:int, name:str, price:float, category:str, in_stock:bool]

products(3):
  1, "Laptop", 3999.90, "Electronics", true
  2, "Mouse", 149.90, "Accessories", true
  3, "Headset", 499.00, "Audio", false
```

**Tokens: ~55 (56% reduction)**

---

## Example 2: RAG Document Chunks with Metadata

### JSON Format
```json
{
  "chunks": [
    {
      "chunk_id": "ch_001",
      "content": "Introduction to artificial intelligence and machine learning systems",
      "page": 1,
      "confidence": 0.95,
      "document_id": "doc_123",
      "language": "en",
      "source": "internal"
    },
    {
      "chunk_id": "ch_002",
      "content": "Neural network architectures for deep learning applications",
      "page": 2,
      "confidence": 0.89,
      "document_id": "doc_123",
      "language": "en",
      "source": "internal"
    }
  ]
}
```

**Tokens: ~180**

### ATON Format
```aton
@schema[chunk_id:str, content:str, page:int, confidence:float, doc_ref:ref]
@defaults[language:"en", source:"internal"]

chunks(2):
  ch_001, "Introduction to artificial intelligence...", 1, 0.95, ->documents[doc_123]
  ch_002, "Neural network architectures for deep...", 2, 0.89, ->documents[doc_123]
```

**Tokens: ~78 (57% reduction)**

---

## Example 3: Multi-Agent System State

### JSON Format
```json
{
  "agents": [
    {
      "agent_id": "rag_001",
      "role": "retriever",
      "status": "active",
      "assigned_tasks": ["t1", "t2", "t5"],
      "last_update": "2024-11-17T10:30:00Z"
    },
    {
      "agent_id": "analyzer_001",
      "role": "analyzer",
      "status": "busy",
      "assigned_tasks": ["t3"],
      "last_update": "2024-11-17T10:29:55Z"
    }
  ],
  "tasks": [
    {
      "task_id": "t1",
      "description": "retrieve_docs",
      "status": "pending",
      "assigned_to": "rag_001"
    },
    {
      "task_id": "t2",
      "description": "extract_entities",
      "status": "in_progress",
      "assigned_to": "rag_001"
    }
  ]
}
```

**Tokens: ~210**

### ATON Format
```aton
@schema[agent_id:str, role:str, status:str, assigned_tasks:ref, last_update:datetime]

agents(2):
  rag_001, "retriever", active, ->tasks[t1,t2,t5], 2024-11-17T10:30:00Z
  analyzer_001, "analyzer", busy, ->tasks[t3], 2024-11-17T10:29:55Z

@schema[task_id:str, description:str, status:str, agent_ref:ref]

tasks(2):
  t1, "retrieve_docs", pending, ->agents[rag_001]
  t2, "extract_entities", in_progress, ->agents[rag_001]
```

**Tokens: ~90 (57% reduction)**

---

## Example 4: User Management with Complex Permissions

### JSON Format
```json
{
  "users": [
    {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "role": "admin",
      "permissions": ["read", "write", "delete"],
      "metadata": {
        "department": "Engineering",
        "location": "Remote",
        "timezone": "UTC"
      },
      "active": true,
      "created": "2024-01-15"
    },
    {
      "id": 2,
      "username": "bob",
      "email": "bob@example.com",
      "role": "user",
      "permissions": ["read"],
      "metadata": {
        "department": "Sales",
        "location": "New York",
        "timezone": "EST"
      },
      "active": true,
      "created": "2024-03-20"
    }
  ]
}
```

**Tokens: ~240**

### ATON Format
```aton
@schema[id:int, username:str, email:str, role:str, permissions:arr, metadata:obj]
@defaults[active:true, created:"2024-01-01"]

users(2):
  1, "alice", "alice@example.com", "admin", ["read","write","delete"], {department:"Engineering",location:"Remote",timezone:"UTC"}, created:"2024-01-15"
  2, "bob", "bob@example.com", "user", ["read"], {department:"Sales",location:"New York",timezone:"EST"}, created:"2024-03-20"
```

**Tokens: ~105 (56% reduction)**

---

## Example 5: AXILIA AI Document Intelligence Pipeline

### JSON Format
```json
{
  "documents": [
    {
      "doc_id": "d_001",
      "filename": "contract_2024.pdf",
      "status": "processed",
      "pages": 45,
      "confidence": 0.98,
      "language": "it",
      "compliance": "GDPR",
      "metadata": {
        "department": "legal",
        "priority": "high",
        "classification": "confidential"
      }
    }
  ],
  "chunks": [
    {
      "chunk_id": "ch_001",
      "document_id": "d_001",
      "page": 1,
      "content": "Article 1: Definitions and Interpretations",
      "entities": ["contract", "legal", "definitions"],
      "embeddings_id": "emb_001"
    }
  ],
  "queries": [
    {
      "query_id": "q_001",
      "timestamp": "2024-11-17T09:00:00Z",
      "query_text": "contratti attivi 2024",
      "results": ["ch_001", "ch_045", "ch_089"],
      "user": "user@axilia.it",
      "response_time_ms": 234
    }
  ]
}
```

**Tokens: ~320**

### ATON Format
```aton
@schema[doc_id:str, filename:str, pages:int, confidence:float, metadata:obj]
@defaults[status:"processed", language:"it", compliance:"GDPR"]

documents(1):
  d_001, "contract_2024.pdf", 45, 0.98, {department:"legal",priority:"high",classification:"confidential"}

@schema[chunk_id:str, doc_ref:ref, page:int, content:str, entities:arr, emb_ref:str]

chunks(1):
  ch_001, ->documents[d_001], 1, "Article 1: Definitions...", ["contract","legal"], emb_001

@schema[query_id:str, timestamp:datetime, query:str, results:ref, user:str, response_ms:int]

queries(1):
  q_001, 2024-11-17T09:00:00Z, "contratti attivi 2024", ->chunks[ch_001,ch_045,ch_089], user@axilia.it, 234
```

**Tokens: ~138 (57% reduction)**

---

## Example 6: Time-Series Data (IoT/Monitoring)

### JSON Format
```json
{
  "sensors": [
    {
      "sensor_id": "temp_01",
      "location": "server_room_a",
      "type": "temperature",
      "unit": "celsius",
      "status": "active"
    },
    {
      "sensor_id": "hum_01",
      "location": "server_room_a",
      "type": "humidity",
      "unit": "percent",
      "status": "active"
    }
  ],
  "readings": [
    {
      "reading_id": "r_001",
      "sensor_id": "temp_01",
      "timestamp": "2024-11-17T10:00:00Z",
      "value": 22.5,
      "quality": "good"
    },
    {
      "reading_id": "r_002",
      "sensor_id": "temp_01",
      "timestamp": "2024-11-17T10:05:00Z",
      "value": 22.7,
      "quality": "good"
    }
  ]
}
```

**Tokens: ~250**

### ATON Format
```aton
@schema[sensor_id:str, location:str, type:str, unit:str]
@defaults[status:"active"]

sensors(2):
  temp_01, "server_room_a", "temperature", "celsius"
  hum_01, "server_room_a", "humidity", "percent"

@schema[reading_id:str, sensor_ref:ref, timestamp:datetime, value:float]
@defaults[quality:"good"]

readings(2):
  r_001, ->sensors[temp_01], 2024-11-17T10:00:00Z, 22.5
  r_002, ->sensors[temp_01], 2024-11-17T10:05:00Z, 22.7
```

**Tokens: ~95 (62% reduction)**

---

## Example 7: Social Network Graph

### JSON Format
```json
{
  "users": [
    {
      "user_id": "u_001",
      "name": "Alice",
      "followers": 1250,
      "following": 340,
      "verified": true
    },
    {
      "user_id": "u_002",
      "name": "Bob",
      "followers": 890,
      "following": 450,
      "verified": false
    }
  ],
  "connections": [
    {
      "from_user": "u_001",
      "to_user": "u_002",
      "type": "follows",
      "since": "2024-01-15"
    },
    {
      "from_user": "u_002",
      "to_user": "u_001",
      "type": "follows",
      "since": "2024-02-20"
    }
  ]
}
```

**Tokens: ~195**

### ATON Format
```aton
@schema[user_id:str, name:str, followers:int, following:int, verified:bool]

users(2):
  u_001, "Alice", 1250, 340, true
  u_002, "Bob", 890, 450, false

@schema[from_ref:ref, to_ref:ref, type:str, since:str]

connections(2):
  ->users[u_001], ->users[u_002], "follows", 2024-01-15
  ->users[u_002], ->users[u_001], "follows", 2024-02-20
```

**Tokens: ~75 (62% reduction)**

---

## Example 8: Financial Transactions

### JSON Format
```json
{
  "accounts": [
    {
      "account_id": "acc_001",
      "holder": "Alice Johnson",
      "type": "checking",
      "currency": "EUR",
      "balance": 15420.50
    },
    {
      "account_id": "acc_002",
      "holder": "Bob Smith",
      "type": "savings",
      "currency": "EUR",
      "balance": 45890.00
    }
  ],
  "transactions": [
    {
      "tx_id": "tx_001",
      "from_account": "acc_001",
      "to_account": "acc_002",
      "amount": 500.00,
      "timestamp": "2024-11-17T10:30:00Z",
      "status": "completed",
      "category": "transfer"
    }
  ]
}
```

**Tokens: ~220**

### ATON Format
```aton
@schema[account_id:str, holder:str, type:str, balance:float]
@defaults[currency:"EUR", status:"active"]

accounts(2):
  acc_001, "Alice Johnson", "checking", 15420.50
  acc_002, "Bob Smith", "savings", 45890.00

@schema[tx_id:str, from_ref:ref, to_ref:ref, amount:float, timestamp:datetime, status:str, category:str]

transactions(1):
  tx_001, ->accounts[acc_001], ->accounts[acc_002], 500.00, 2024-11-17T10:30:00Z, "completed", "transfer"
```

**Tokens: ~90 (59% reduction)**

---

## Token Savings Summary

| Use Case | JSON Tokens | ATON Tokens | Reduction |
|----------|-------------|-------------|-----------|
| E-commerce | 125 | 55 | 56% |
| RAG Chunks | 180 | 78 | 57% |
| Multi-Agent | 210 | 90 | 57% |
| User Management | 240 | 105 | 56% |
| Document Intelligence | 320 | 138 | 57% |
| Time-Series | 250 | 95 | 62% |
| Social Network | 195 | 75 | 62% |
| Financial | 220 | 90 | 59% |
| **Average** | **218** | **91** | **58%** |

---

## When to Use ATON

✅ **Use ATON for:**
- RAG systems with large retrieval sets
- Multi-agent communication
- High-volume API calls to LLMs
- Document processing pipelines
- Time-series data with many readings
- Graph data with relationships
- Any scenario where token cost matters

❌ **Don't use ATON for:**
- Single small objects
- Public APIs (stick with JSON for compatibility)
- Binary data (use Protocol Buffers)
- Human-edited configuration files
- When you need universal tool support

---

## Migration Guide

### From JSON to ATON

1. **Identify homogeneous arrays** - these benefit most
2. **Extract common patterns** - use @defaults
3. **Add type hints** - use @schema for clarity
4. **Define relationships** - use -> for references
5. **Test token counts** - verify actual savings

### From TOON to ATON

1. **Add type information** - TOON has no types
2. **Enable nesting** - ATON supports complex objects
3. **Add relationships** - link related entities
4. **Use defaults** - optimize repeated values

---

*For more examples and the full specification, see the ATON Whitepaper.*
