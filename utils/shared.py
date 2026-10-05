import ast
import re
import unicodedata
from pathlib import Path

import pandas as pd

email_pattern = (
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

phone_pattern = (
    r"\b(?:\+?1[-.\s]?)?"
    r"(?:\(?\d{3}\)?[-.\s]?)"
    r"\d{3}[-.\s]?\d{4}\b"
)

ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
MAJORITY = "technical support"


def filter_pii(text):

    if pd.isna(text):
        return text

    text = re.sub(email_pattern, "[EMAIL]", text)

    text = re.sub(phone_pattern, "[PHONE]", text)

    text = re.sub(ssn_pattern, "[SSN]", text)

    return text


def clean_whitespace(text: str) -> str:
    if pd.isnull(text) or pd.isna(text):
        return text

    return re.sub(r"[\s\t\n\r\f\v]+", " ", text).strip()


def normalize_unicode(text: str) -> str:
    if pd.isnull(text) or pd.isna(text):
        return text

    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def normalize_text_column(df: pd.DataFrame, column: str, id_column: str = "ticket_id"):
    """Strip and lowercase a categorical column. Returns the change mask and sample ids."""
    print(f"{column}: {df[column].value_counts()}")
    original = df[column].copy()
    df[column] = df[column].astype("string").str.strip().str.lower()
    changed_mask = original.astype("string") != df[column]
    changed_ids = df.loc[changed_mask, id_column].head(5).tolist()
    print(f"{column} values changed:", int(changed_mask.sum()))
    print(f"{column} IDs: {changed_ids}")
    return {
        "changed_mask": changed_mask,
        "changed_ids": changed_ids,
    }


def steps_divider(text: str) -> str:
    txt = f"# ------------------------------------------------\n# {text}\n# ------------------------------------------------"
    return txt


def parse_tags(val):
    if pd.isnull(val) or pd.isna(val):
        return []

    try:
        parsed = ast.literal_eval(val)

        if isinstance(parsed, list):
            return parsed
        return []
    except (ValueError, SyntaxError):
        return []


def normalize_tags(tags: list[str]) -> list[str]:
    return [tag.strip().lower() for tag in tags]


def findings_table(logs: list[dict]) -> str:
    lines = [
        "| Decision | Action | Records |",
        "| --- | --- | ---: |",
    ]
    for record in logs:
        lines.append(
            f"| {record['issue']} | {record['action']} | {int(record['affected_count'])} |"
        )
    return "\n".join(lines)


def findings_sections(logs: list[dict]) -> str:
    parts = []
    for number, record in enumerate(logs, start=1):
        ids = ", ".join(str(ticket_id) for ticket_id in record["representative_ids"])
        parts.append(
            "\n".join(
                [
                    f"## {number}. {record['issue']}",
                    "",
                    f"**What the issue was.** {record['issue']}",
                    "",
                    f"**Why it is an issue.** {record['reason']}",
                    "",
                    f"**How it was addressed.** {record['action']}",
                    "",
                    f"**Records affected.** {int(record['affected_count'])}",
                    "",
                    f"**Representative ticket ids.** {ids or 'none'}",
                    "",
                    f"**Risk.** {record['risk_or_limitation']}",
                ]
            )
        )
    return "\n\n".join(parts)


def write_findings(logs: list[dict], path: Path) -> None:
    path.write_text(
        "# Task 1 — Cleaning findings\n\n"
        + findings_table(logs)
        + "\n\n"
        + findings_sections(logs),
        encoding="utf-8",
    )


def score_words(counts, label, total_trained):
    rows = []
    for word, in_class in counts[label].items():
        out_of_class = sum(counts[other][word] for other in counts if other != label)
        majority_hits = counts[MAJORITY][word]
        gain = in_class - majority_hits
        if gain <= 0:
            continue
        matched = in_class + out_of_class
        rows.append(
            {
                "department": label,
                "phrase": word,
                "in_class": in_class,
                "out_of_class": out_of_class,
                "majority_hits": majority_hits,
                "gain": gain,
                "precision": in_class / matched,
                "coverage": matched / total_trained,
            }
        )
    rows.sort(key=lambda row: row["gain"], reverse=True)
    return rows


def words_in(text):
    return set(re.findall(r"[a-z0-9']+", str(text).lower()))


def score_phrase(trained_df, department, phrase):
    text = trained_df["body"].fillna("").str.lower()
    department_column = trained_df["department"]
    matches = text.str.contains(phrase.lower(), regex=False)
    in_class = int((matches & (department_column == department)).sum())
    out_of_class = int((matches & (department_column != department)).sum())
    majority_hits = int((matches & (department_column == MAJORITY)).sum())
    matched = in_class + out_of_class
    return {
        "department": department,
        "phrase": phrase,
        "in_class": in_class,
        "out_of_class": out_of_class,
        "majority_hits": majority_hits,
        "gain": in_class - majority_hits,
        "precision": (in_class / matched) if matched else 0,
        "coverage": matched / len(trained_df),
    }
