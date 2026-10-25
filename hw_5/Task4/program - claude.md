# Task 4 - Build the Vector Store - claude

Save the code block below as `build_store.py` in this folder. Run it with `python build_store.py` **after** Task 3 has written `../Task3/records.json`. It builds a persistent store in the folder `lancedb` next to the script, then runs a self-check.

You must first set up the course environment from `VECTOR_STORE_SETUP.md` (pinned embedding model, LanceDB, FastEmbed). I could not run this code on my machine because those packages are not installed there, so I did not verify the output below.

## Logic (read this before the code)

1. **Load** the Task 3 records from `records.json`.
2. **Create** a `VectorStore` and give it a folder path. LanceDB makes the database in that folder, or reopens it if it exists.
3. **Call `build(records)`.** The supplied class does the rest:
   - rejects empty input and repeated `chunk_id` values,
   - turns each `embedding_text` into a vector with the course model,
   - stores the vector, the unchanged `content`, and the `metadata` in the table `homework5_chunks`,
   - overwrites the table, so a rebuild never adds duplicates.
4. **Do not edit `VectorStore.py`.** The course fixes the model, the library, and cosine distance. Tasks 5 and 6 call the same class.
5. **Self-check.** Open the store again as a new object (proves it was saved to disk). Take every 20th chunk. Search with that chunk's own text. The chunk must come back at rank 1.

## Why this design

**Why a self-check.** If the folder does not open, an ID is lost, or text is stored under the wrong ID, then every later result is wrong. This check finds that before any labeling starts.

**Why the chunk's own text.** A chunk is the closest thing to itself. If it is not rank 1 for its own text, something is broken.

**Why only `embedding_text` is embedded.** Search needs the title and product. The model later needs the clean `content`. The class keeps both.

## Code

```python
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
RECORDS = HW5 / "Task3" / "records.json"
DB = HERE / "lancedb"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"


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
```

## What each part of the code does

| Part | What it does |
| --- | --- |
| `load_vector_store_class` | Imports the supplied class from its file path. The file is not changed. |
| `build` | Creates the store and calls `build(records)` once. |
| `self_check` | Reopens the store, searches with the text of every 20th chunk, and counts chunks that are not rank 1. |
| `main` | Runs both and stops with an error if the check fails. |

## Expected result

The terminal prints `built 134 records into lancedb`, then one `PASS` line per sample, then `self-check passed`. If a line says `FAIL`, open Task 3 first: look for two chunks with almost the same text.
