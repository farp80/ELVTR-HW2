import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT.parent / "knowledge_base"
RESULT_PATH = ROOT / "records.json"

def read_front_matter(text):
    """Return the header fields and the text that follows the header."""
    _, header, body = text.split("---", 2)
    fields = {}
    for line in header.strip().splitlines():
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body

def sections(body):
    """Split the article on its markdown headings. Keep each heading with its text."""
    chunks = []
    current = []
    for line in body.splitlines(keepends=True):
        if line.startswith("## ") and current:
            chunks.append("".join(current).strip("\n"))
            current = [line]
        elif line.startswith("## "):
            current = [line]
        elif current:
            current.append(line)
    if current:
        chunks.append("".join(current).strip("\n"))
    return chunks

def build_records():
    parsed = []
    for path in ARTICLES.glob("*.txt"):
        fields, body = read_front_matter(path.read_text(encoding="utf-8"))
        parsed.append((fields, sections(body)))
    parsed.sort(key=lambda item: item[0]["article_id"])

    records = []
    for fields, parts in parsed:
        for position, content in enumerate(parts):
            records.append(
                {
                    "chunk_id": f"{fields['article_id']}-{position}",
                    "embedding_text": f"{fields['title']}. {fields['product']}. {content}",
                    "content": content,
                    "metadata": {
                        "article_id": fields["article_id"],
                        "title": fields["title"],
                        "chunk_position": position,
                    },
                }
            )
    return records

if __name__ == "__main__":
    records = build_records()
    RESULT_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(records)} chunks written to {RESULT_PATH.name}")