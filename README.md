# Persistent Key Value Store

This project implements a **network-accessible persistent key/value storage system** using only the standard libraries of Python.

The system provides the following operations:

- Put(Key, Value)
- Read(Key)
- ReadKeyRange(StartKey, EndKey)
- BatchPut(keys, values)
- Delete(Key)

The storage engine is designed to provide:

- Low latency reads and writes
- High write throughput
- Support for datasets larger than RAM
- Crash-safe persistence
- Predictable behavior under load

---

# Architecture

```
                 Client
                   |
                   v
              HTTP Server
                (app/server.py)
                   |
                   v
              Request Handler
                (app/handlers.py)
                   |
                   v
            Storage Engine
             (storage/engine.py)
                   |
        --------------------------------
        |              |               |
        v              v               v
 Write Ahead Log     MemTable        SSTables
     wal.log        (In Memory)       (Disk)
```

---

# Storage Components

## Write Ahead Log (WAL)

All writes are first appended to a **Write Ahead Log** to ensure durability.

```
Put(key,value)
      |
      v
Append to WAL
      |
      v
Update MemTable
```

If the system crashes, the WAL can be replayed to recover the latest writes.

---

## MemTable

The MemTable is an **in-memory data structure** used to store recent writes.

Characteristics:

- Maintains sorted keys
- Provides fast reads and writes
- Acts as the first lookup point for reads

When the MemTable reaches a threshold, it is **flushed to disk**.

---

## SSTables

When the MemTable reaches the configured limit, its contents are written to disk as **SSTables (Sorted String Tables)**.

Example file:

```
data/sstable_0.db
```

Example content:

```
{"key":"user1","value":"Annu"}
{"key":"user2","value":"data"}
```

SSTables are **immutable files stored on disk** that allow the system to handle datasets larger than RAM.

---

# Write Flow

```
Client
  |
PUT(key,value)
  |
HTTP Server
  |
Append to WAL
  |
Update MemTable
  |
If MemTable limit reached
  |
Flush to SSTable
```

This ensures fast sequential disk writes and durability.

---

# Read Flow

```
Client
  |
Read(key)
  |
Check MemTable
  |
If not found
  |
Search SSTables
(newest → oldest)
```

The system checks newer SSTables first to return the latest value.

---

# Range Query Flow

```
Client
  |
ReadKeyRange(start,end)
  |
Check MemTable
  |
Merge results with SSTables
  |
Return sorted keys
```

Range queries leverage the sorted structure of the MemTable.

---

# Crash Recovery

When the server restarts:

```
Restart Server
      |
Load existing SSTables
      |
Replay WAL entries
      |
Rebuild MemTable
```

This guarantees that **no committed writes are lost**.

---

# API Endpoints

The server exposes HTTP endpoints running on:

```
http://localhost:8080
```

---

## Put

Store a key-value pair.

```
POST /put
```

Example:

```bash
curl -X POST http://localhost:8080/put \
-H "Content-Type: application/json" \
-d '{"key":"user1","value":"Annu"}'
```

Response:

```
{"status":"ok"}
```

---

## Read

Retrieve a value for a key.

```
GET /read?key=<key>
```

Example:

```bash
curl "http://localhost:8080/read?key=user1"
```

Response:

```
{"value":"Annu"}
```

---

## Range Query

Retrieve all keys within a given range.

```
GET /range?start=<startKey>&end=<endKey>
```

Example:

```bash
curl "http://localhost:8080/range?start=a&end=z"
```

---

## Batch Put

Insert multiple key-value pairs.

```
POST /batch_put
```

Example:

```bash
curl -X POST http://localhost:8080/batch_put \
-H "Content-Type: application/json" \
-d '{
"items":[
{"key":"a","value":"1"},
{"key":"b","value":"2"}
]
}'
```

---

## Delete

Delete a key.

```
DELETE /delete/<key>
```

Example:

```bash
curl -X DELETE http://localhost:8080/delete/user1
```

Deletion is implemented using **tombstones**.

---

# Project Structure

```
kv-store/
│
├── app/
│   ├── server.py
│   ├── handlers.py
│   └── config.py
│
├── storage/
│   └── engine.py
│
├── data/
│
├── tests/
│   ├── test_engine.py
│   └── test_api.py
│
├── run.py
└── README.md
```

| Component | Description |
|--------|--------|
| server.py | HTTP server |
| handlers.py | request handlers |
| config.py | configuration |
| engine.py | storage engine |
| data/ | persistent storage |
| tests/ | unit tests |

---

# Running the Project

## 1. Install Python

Install **Python 3.8 or higher**.

Verify installation:

```
python --version
```

---

## 2. Clone the Repository

```
git clone https://github.com/annuyadav/kv-store.git
cd kv-store
```

---

## 3. Start the Server

```
python run.py
```

Server will start on:

```
http://localhost:8080
```

---

# Running Tests

Run all tests:

```
python -m unittest discover tests
```

Example output:

```
Ran 6 tests in 0.7s
OK
```

---


# Data Persistence

Data is stored in two locations:

| File | Purpose |
|-----|--------|
| wal.log | crash recovery log |
| data/sstable_*.db | persistent storage |

---

# Design Tradeoffs

Advantages:

- High write throughput using sequential logging
- Durable storage via WAL
- Ability to store datasets larger than memory
- Simple architecture

Limitations:

- Read amplification due to multiple SSTables
- No bloom filters
- No SSTable indexing
- No distributed replication

---

# Future Improvements

Possible enhancements include:

- Bloom filters for faster reads
- SSTable indexing
- Background compaction
- Distributed replication
- Horizontal sharding

---

# References

The design is inspired by modern storage systems and research papers on LSM Trees and distributed databases.
