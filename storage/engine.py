import os
import json
import bisect
from app.config import DATA_DIR, WAL_FILE, MEMTABLE_LIMIT


class StorageEngine:

    def __init__(self):
        self.memtable = {}
        self.sorted_keys = []
        self.sstables = []

        os.makedirs(DATA_DIR, exist_ok=True)

        self._load_sstables()
        self._recover_wal()

    def _load_sstables(self):
        files = sorted(os.listdir(DATA_DIR))
        for f in files:
            self.sstables.append(os.path.join(DATA_DIR, f))

    def _recover_wal(self):

        if not os.path.exists(WAL_FILE):
            return

        with open(WAL_FILE, "r") as f:
            for line in f:
                entry = json.loads(line)
                key = entry["key"]
                value = entry["value"]

                self.memtable[key] = value

                if key not in self.sorted_keys:
                    bisect.insort(self.sorted_keys, key)

    def _append_wal(self, key, value):

        with open(WAL_FILE, "a") as f:
            f.write(json.dumps({"key": key, "value": value}) + "\n")

    def put(self, key: str, value: str):

        self._append_wal(key, value)

        self.memtable[key] = value

        if key not in self.sorted_keys:
            bisect.insort(self.sorted_keys, key)

        if len(self.memtable) >= MEMTABLE_LIMIT:
            self._flush()


    def read(self, key: str):

    	if key in self.memtable:
            value = self.memtable[key]

            if value == "__DELETE__":
                return None

            return value

    	for sstable in reversed(self.sstables):

            with open(sstable) as f:

                for line in f:
                    entry = json.loads(line)

                    if entry["key"] == key:
                        value = entry["value"]

                        if value == "__DELETE__":
                            return None

                        return value
            return None
        
    
    def delete(self, key: str):
        self.put(key, "__DELETE__")

    def read_range(self, start: str, end: str):

        result = {}

        for key in self.sorted_keys:

            if start <= key <= end:

                value = self.memtable[key]

                if value != "__DELETE__":
                    result[key] = value

        return result

    def batch_put(self, items):

        for key, value in items:
            self.put(key, value)

    def _flush(self):

        filename = os.path.join(DATA_DIR, f"sstable_{len(self.sstables)}.db")

        with open(filename, "w") as f:

            for key in sorted(self.memtable.keys()):
                value = self.memtable[key]

                f.write(json.dumps({"key": key, "value": value}) + "\n")

        self.sstables.append(filename)

        self.memtable.clear()
        self.sorted_keys.clear()

        open(WAL_FILE, "w").close()