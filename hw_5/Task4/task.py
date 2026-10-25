import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HW5 = ROOT.parent
RECORDS = HW5 / "Task3" / "records.json"
DB = ROOT / "lancedb"
HELPER = HW5 / "Fidel Alejandro Rosell Perez - VectorStore.py"

def load_vector_store_class():
    # The helper file name has spaces, so import it by path.
    spec = importlib.util.spec_from_file_location("vector_store_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore


def build(records):
    VectorStore = load_vector_store_class()
    store = VectorStore(DB)
    store.build(records)  # embeds embedding_text, saves content + metadata
    return len(records)


def self_check(records):
    VectorStore = load_vector_store_class()
    store = VectorStore(DB)  # new object: reopens the saved database
    failures = 0
    for record in records[::20]:
        hits = store.query(record["content"], top_k=1)
        found = hits[0]["chunk_id"]
        ok = found == record["chunk_id"]
        failures += 0 if ok else 1
        print("PASS" if ok else "FAIL", record["chunk_id"], "->", found)
    return failures


def main():
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    print("built", build(records), "records into", DB.name)
    failures = self_check(records)
    if failures:
        raise SystemExit(f"{failures} self-check failures")
    print("self-check passed")


if __name__ == "__main__":
    main()