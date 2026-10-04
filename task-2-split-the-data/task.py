import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.pandas_utils import PandasUtils

panda_base = PandasUtils(
    file_path=r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
)
data_cleaned = panda_base.df

# --------- POLICY --------------
TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15
SEED = 42

rng = random.Random(SEED)

split_records = []

for department, group in data_cleaned.groupby("department"):
    ticket_ids = group["ticket_id"].tolist()
    rng.shuffle(ticket_ids)
    n = len(ticket_ids)
    train_end = int(n * TRAIN_RATIO)
    validation_end = train_end + int(n * VALIDATION_RATIO)

    for ticket_id in ticket_ids[:train_end]:
        split_records.append({"ticket_id": ticket_id, "split": "train"})

    for ticket_id in ticket_ids[train_end:validation_end]:
        split_records.append({"ticket_id": ticket_id, "split": "validation"})

    for ticket_id in ticket_ids[validation_end:]:
        split_records.append({"ticket_id": ticket_id, "split": "test"})

splitted_df = panda_base.create_dataframe(split_records, columns=["ticket_id", "split"])
print(splitted_df.head())

splitted_df.to_csv(
    r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_splitted.csv",
    index=False,
)

# -- splitted columns check --
assert list(splitted_df.columns) == ["ticket_id", "split"]
assert set(splitted_df["split"].unique()) == {"train", "validation", "test"}
assert len(splitted_df) == len(data_cleaned)
assert splitted_df["ticket_id"].nunique() == len(data_cleaned)
assert splitted_df["ticket_id"].is_unique
print(splitted_df["split"].value_counts(normalize=True))
print("Splitted columns check passed")

original_pandas = PandasUtils(
    file_path=r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets.csv"
)
original_df = original_pandas.df

df_with_split = original_df.merge(splitted_df, on="ticket_id", how="left")
df_with_split.columns.str.lower()
df_with_split.columns = df_with_split.columns.str.lower()
print(df_with_split.columns)
print(df_with_split.groupby("split")["department"].value_counts(normalize=True))
print(original_pandas.df["Department"].value_counts(normalize=True))
print("Original and splitted departments distribution check passed")
