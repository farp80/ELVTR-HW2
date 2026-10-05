import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.log import Logs
from utils.pandas_utils import PandasUtils
from utils.shared import (
    clean_whitespace,
    email_pattern,
    filter_pii,
    normalize_tags,
    normalize_text_column,
    normalize_unicode,
    parse_tags,
    phone_pattern,
    ssn_pattern,
    steps_divider,
    write_findings,
)

if __name__ == "__main__":
    kwargs = {
        "file_path": r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets.csv"
    }

    logs = Logs(**kwargs)
    pandas_utils = PandasUtils(**kwargs)
    print(steps_divider("1. Inspect columns and make them standarized"))

    columns_changes = []
    original_columns = pandas_utils.df.columns.tolist()
    print(f"Original columns: {original_columns}")

    standarized_columns = pandas_utils.column_standarization()
    print(f"Standarized columns: {standarized_columns}")

    for original, cleaner in zip(original_columns, standarized_columns):
        if original != cleaner:
            columns_changes.append({"original": original, "cleaner": cleaner})

    logs.log_decision(
        issue="Inconsistent column name formatting",
        action="Standardized column names to lowercase snake_case",
        reason="Creates consistent field names and makes downstream processing easier.",
        affected_count=len(columns_changes),
        representative_ids=[],
        risk_or_limitation="Column names are changed only; the underlying record values are not modified.",
    )

    print(logs.logs)
    print("*" * 60)

    print(steps_divider("2. Normalize whitespace and encoding "))
    encoding_mask = pandas_utils.df["body"].notna() & pandas_utils.df["body"].apply(
        lambda x: unicodedata.normalize("NFKC", str(x)) != str(x)
    )

    print("Records affected by Unicode normalization:", encoding_mask.sum())

    whitespace_mask = pandas_utils.df["body"].apply(
        lambda x: isinstance(x, str) and bool(re.search(r"\s{2,}|\n|\t|^\s|\s$", x))
    )

    print(pandas_utils.df.loc[whitespace_mask, ["ticket_id", "body"]].head(10))

    whitespace_ids = pandas_utils.df.loc[whitespace_mask, "ticket_id"].tolist()

    print(f"Whitespace IDs: {whitespace_ids}")

    # Data parsing and structuring
    body = pandas_utils.df["body"]
    missing_body_mask = body.isna() | (body.fillna("").str.strip() == "")

    print(f"Missing/empty bodies: {missing_body_mask.sum()}")

    print(pandas_utils.df.loc[missing_body_mask, ["ticket_id", "body"]])

    body_ids = pandas_utils.df.loc[missing_body_mask, "ticket_id"].tolist()

    print(f"Body IDs: {body_ids}")

    body_count = missing_body_mask.sum()
    print(f"Body count: {body_count}")

    pandas_utils.df = pandas_utils.df.loc[~missing_body_mask].copy()

    logs.log_decision(
        issue="Missing or empty ticket body",
        action="Dropped records",
        reason="Body is the primary text input for the ticket classification model.",
        affected_count=body_count,
        representative_ids=body_ids,
        risk_or_limitation="Removing records may introduce bias if missing bodies are associated with particular departments.",
    )

    if whitespace_mask.sum() > 0:
        logs.log_decision(
            issue="Inconsistent whitespace in ticket text",
            action="Normalized repeated whitespace, tabs, line breaks, and leading/trailing spaces",
            reason="Whitespace variations do not normally add meaning to support-ticket text and can create unnecessary textual variation.",
            affected_count=whitespace_mask.sum(),
            representative_ids=whitespace_ids,
            risk_or_limitation="Some unusual whitespace may have intentional formatting meaning, although this is unlikely in ordinary ticket text.",
        )

    encoding_ids = pandas_utils.df.loc[encoding_mask, "ticket_id"].head(5).tolist()
    print(f"Encoding IDs: {encoding_ids}")

    if encoding_mask.sum() > 0:
        logs.log_decision(
            issue="Unicode normalization issue in ticket text",
            action="Normalized Unicode characters to their standard form",
            reason="Unicode normalization ensures consistent representation of characters across systems.",
            affected_count=encoding_mask.sum(),
            representative_ids=encoding_ids,
            risk_or_limitation="Some Unicode characters may have intentional formatting meaning, although this is unlikely in ordinary ticket text.",
        )

    pandas_utils.df.loc[encoding_mask, "body"] = pandas_utils.df.loc[
        encoding_mask, "body"
    ].apply(normalize_unicode)

    pandas_utils.df.loc[whitespace_mask, "body"] = pandas_utils.df.loc[
        whitespace_mask, "body"
    ].apply(clean_whitespace)

    print(steps_divider("3. Parse and structure department data"))
    # -------- department, priority -----------------------------------------
    parsing_columns = ["department", "priority"]

    for c in parsing_columns:
        settings = normalize_text_column(pandas_utils.df, c)

        if settings["changed_mask"].sum() > 0 or len(settings["changed_ids"]) > 0:
            logs.log_decision(
                issue=f"Inconsistent {c} formatting",
                action="Trimmed whitespace and normalized casing",
                reason=f"{c} is a categorical field and equivalent values should use a consistent representation.",
                affected_count=settings["changed_mask"].sum(),
                representative_ids=settings["changed_ids"],
                risk_or_limitation="Changing casing is safe for categorical normalization, but semantically different labels must not be merged without domain evidence.",
            )

    invalid_priority_mask = ~pandas_utils.df["priority"].isin(["low", "medium", "high"])
    print(f"Invalid priority: {invalid_priority_mask.sum()}")

    invalid_priority_ids = pandas_utils.df.loc[
        invalid_priority_mask, ["ticket_id", "priority"]
    ].head(20)

    # ------------ tags ------------------------------------
    print(pandas_utils.df["tags"].iloc[0])
    pandas_utils.df["tags"] = pandas_utils.df["tags"].apply(parse_tags)
    print(pandas_utils.df["tags"].iloc[0])
    pandas_utils.df["tags"] = pandas_utils.df["tags"].apply(normalize_tags)
    print(pandas_utils.df["tags"].iloc[0])

    # ------------ PII ------------------------------------
    print(steps_divider("4. Filter PII"))
    pii_mask = (
        pandas_utils.df["body"].str.contains(email_pattern, regex=True, na=False)
        | pandas_utils.df["body"].str.contains(phone_pattern, regex=True, na=False)
        | pandas_utils.df["body"].str.contains(ssn_pattern, regex=True, na=False)
    )
    print(f"PII mask: {pii_mask.sum()}")

    pandas_utils.df.loc[pii_mask, "body"] = pandas_utils.df.loc[pii_mask, "body"].apply(
        filter_pii
    )
    print(pandas_utils.df.loc[pii_mask, ["ticket_id", "body"]].head(10))

    pii_ids = pandas_utils.df.loc[pii_mask, "ticket_id"].tolist()
    print(f"PII IDs: {pii_ids}")

    logs.log_decision(
        issue="PII found in ticket text",
        action="Filtered PII",
        reason="PII should not be stored in the database.",
        affected_count=pii_mask.sum(),
        representative_ids=pii_ids,
        risk_or_limitation="PII may be sensitive and should not be stored in the database.",
    )

    body = pandas_utils.df["body"]
    body_patterns = [
        {
            "issue": "HTML break tags",
            "pattern": r"<br\s*/?>",
            "reason": "Break tags are template markup and do not describe the customer's request.",
            "risk_or_limitation": "The pattern is limited to br so it does not delete other tags.",
        },
        {
            "issue": "Broken break markers",
            "pattern": r"<brWarm|brbr",
            "reason": "These closings are a line break written without a finished br tag.",
            "risk_or_limitation": "Only the broken <brWarm tag and the doubled brbr run are matched.",
        },
        {
            "issue": "Missing space after sentence punctuation",
            "pattern": r"[.!?][A-Z]",
            "reason": "Two sentences were concatenated, so the model sees one token instead of two.",
            "risk_or_limitation": "The next character must be a capital, so names such as Node.js stay intact.",
        },
        {
            "issue": "Missing space after a comma",
            "pattern": r",[A-Za-z]",
            "reason": "The comma is glued to the next word in openings and signature lines.",
            "risk_or_limitation": "The space is inserted at the first letter only, so nameacc_num stays one token.",
        },
        {
            "issue": "Curly single quotes",
            "pattern": r"[’‘]",
            "reason": "A curly apostrophe and an ASCII apostrophe are the same word with two code points.",
            "risk_or_limitation": "The curly mark is treated as an apostrophe.",
        },
        {
            "issue": "Square-bracket template slots",
            "pattern": r"\[[^\]]+\]",
            "reason": "Bracketed slots such as [Your Name] are unfilled template fields.",
            "risk_or_limitation": "A broad bracket pattern also matches a JSON fragment that names a real product.",
        },
        {
            "issue": "Angle-bracket placeholders",
            "pattern": r"<[^>]+>",
            "reason": "Angle-bracket slots such as <tel_num> and <name> are redacted fields written as markup.",
            "risk_or_limitation": "This pattern also matches break tags, so those rows are counted here as well.",
        },
    ]

    for index, item in enumerate(body_patterns):
        mask = body.str.contains(item["pattern"], regex=True, na=False)
        affected_count = int(mask.sum())
        print(f"{item['issue']}: {affected_count}")

        if affected_count == 0:
            continue

        action = "replace PII" if index == len(body_patterns) - 1 else "change"
        representative_ids = pandas_utils.df.loc[mask, "ticket_id"].head(5).tolist()

        if item["issue"] == "Square-bracket template slots":
            pandas_utils.df["body"] = pandas_utils.df["body"].str.replace(
                item["pattern"], "[PLACEHOLDER]", regex=True
            )

        logs.log_decision(
            issue=item["issue"],
            action=action,
            reason=item["reason"],
            affected_count=affected_count,
            representative_ids=representative_ids,
            risk_or_limitation=item["risk_or_limitation"],
        )

    pandas_utils.df = pandas_utils.df.dropna(subset=["body"])
    pandas_utils.df = pandas_utils.df[pandas_utils.df["body"].str.strip() != ""]

    df_cleaned_dataset = pandas_utils.df.copy()
    df_cleaned_dataset.to_csv(
        r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv",
        index=False,
    )

    print(steps_divider("5. Export cleaned dataset"))
    print(f"Cleaned dataset head: {df_cleaned_dataset.head(10)}")
    print(f"Cleaned dataset tail: {df_cleaned_dataset.tail(10)}")
    print(f"Cleaned dataset columns: {df_cleaned_dataset.columns}")
    print(f"Cleaned dataset dtypes: {df_cleaned_dataset.dtypes}")
    print(f"Cleaned dataset info: {df_cleaned_dataset.info()}")
    print(f"Empty body: {df_cleaned_dataset['body'].isna().sum()}")
    print(f"Empty body: {df_cleaned_dataset['body'].str.strip().eq('').sum()}")

    write_findings(
        logs.logs,
        Path(
            r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - cleaning_log_findings.md"
        ),
    )
