import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HW2_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.classes.rule_based import RuleBasedBaseline

from shared.utils.pandas_utils import PandasUtils

data_cleaned_base = PandasUtils(
    file_path=PROJECT_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
)
splitted_base = PandasUtils(
    file_path=HW2_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_splitted.csv"
)

current_df = data_cleaned_base.df.merge(splitted_base.df, on="ticket_id", how="left")

trained_df = current_df[current_df["split"] == "train"].copy()
total_rows = len(trained_df)
constant_baseline = int(
    trained_df["department"].value_counts().loc["technical support"]
)
percentage_constant_baseline = constant_baseline / total_rows * 100

trained_df.to_csv(
    HW2_ROOT / "Fidel Alejandro Rosell Perez - trained_df.csv",
    index=False,
)

with open(HW2_ROOT / "possible_baselinerules.json", encoding="utf-8") as file:
    settings = json.load(file)

MAJORITY = settings["majority_department"]
rules = settings["rules"]

model = RuleBasedBaseline(MAJORITY, rules)
model_path = HW2_ROOT / "Fidel Alejandro Rosell Perez - rule_based_baseline.pkl"
model.save(model_path)

loaded = RuleBasedBaseline.load(model_path)
print(loaded.predict("The platform has an engagement problem"))
print(loaded.predict("The switches experienced inaccessibility"))
print(loaded.predict("Thank you for your help"))

correct = 0

for body, actual in zip(trained_df["body"].fillna(""), trained_df["department"]):
    if loaded.predict(body) == actual:
        correct += 1

print("-" * 60)
print(f" Total rows: {total_rows}")
print(f" Constant baseline: {constant_baseline}")
print(f" Percentage constant baseline: {percentage_constant_baseline:.2f}%")
print(f" Ruled based baseline: {correct}")
print(f" Percentage ruled based baseline: {correct / total_rows * 100:.2f}%")
print(f" Improvement: {correct / total_rows * 100 - percentage_constant_baseline:.2f}%")
