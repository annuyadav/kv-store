import os
import json
import bisect

DATA_DIR = "data"
WAL_FILE = "wal.log"
MEMTABLE_LIMIT = 5


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

                if value == "__DELETE__":
                    self.memtable[key] = None
                else:
                    self.memtable[key] = value

                if key not in self.sorted_keys:
                    bisect.insort(self.sorted_keys, key)

    def _append_wal(self, key, value):
        with open(WAL_FILE, "a") as f:
            f.write(json.dumps({"key": key, "value": value}) + "\n")

    def put(self, key, value):
        self._append_wal(key, value)

        self.memtable[key] = value

        if key not in self.sorted_keys:
            bisect.insort(self.sorted_keys, key)

        if len(self.memtable) >= MEMTABLE_LIMIT:
            self._flush()

    def batch_put(self, items):
        for key, value in items:
            self.put(key, value)

    def delete(self, key):
        self.put(key, "__DELETE__")

    def read(self, key):

        if key in self.memtable:
            value = self.memtable[key]
            return None if value == "__DELETE__" else value

        for sstable in reversed(self.sstables):
            with open(sstable) as f:
                for line in f:
                    entry = json.loads(line)
                    if entry["key"] == key:
                        value = entry["value"]
                        return None if value == "__DELETE__" else value

        return None

    def read_range(self, start, end):

        result = {}

        for key in self.sorted_keys:
            if start <= key <= end:
                val = self.memtable.get(key)
                if val != "__DELETE__":
                    result[key] = val

        for sstable in reversed(self.sstables):
            with open(sstable) as f:
                for line in f:
                    entry = json.loads(line)
                    key = entry["key"]

                    if start <= key <= end and key not in result:
                        val = entry["value"]
                        if val != "__DELETE__":
                            result[key] = val

        return result

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