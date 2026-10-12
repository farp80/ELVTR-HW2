"""Task 3 — Build a Constant Baseline.

Baseline that always predicts one department.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HW2_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from shared.classes.constant_baseline_class import ConstantBaseline

from shared.utils.pandas_utils import PandasUtils

data_cleaned_base = PandasUtils(
    file_path=PROJECT_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
)
splitted_base = PandasUtils(
    file_path=HW2_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_splitted.csv"
)

df = data_cleaned_base.df.merge(splitted_base.df, on="ticket_id", how="left")
print(df.head())

constant_baseline = ConstantBaseline(
    df,
    "train",
    HW2_ROOT / "Fidel Alejandro Rosell Perez - constant_baseline.pkl",
)
constant_baseline.fit()
constant_baseline.save()

constant_baseline_loaded = ConstantBaseline.load(
    HW2_ROOT / "Fidel Alejandro Rosell Perez - constant_baseline.pkl",
)

print(constant_baseline_loaded.predict("I have a problem with my computer"))
print(constant_baseline_loaded.predict("I have a problem with my phone"))
print(constant_baseline_loaded.predict("I have a problem with my tablet"))
print(constant_baseline_loaded.predict("I have a problem with my laptop"))
print(constant_baseline_loaded.predict("I have a problem with my desktop"))
print(constant_baseline_loaded.predict("I have a problem with my printer"))
print(constant_baseline_loaded.predict("I have a problem with my scanner"))
print(constant_baseline_loaded.predict("I have a problem with my fax machine"))
print(constant_baseline_loaded.predict("I have a problem with my copier"))
print(constant_baseline_loaded.predict(""))
print(constant_baseline_loaded.predict(None))

selected_label = constant_baseline_loaded.department
print(f"Selected label: {selected_label}")
percentage = (
    constant_baseline_loaded.trained_df["department"] == selected_label
).mean()
print(f"Percentage of training records that have the selected label: {percentage}")
