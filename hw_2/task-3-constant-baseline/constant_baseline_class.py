import pickle

import pandas as pd


class ConstantBaseline:
    def __init__(self, df: pd.DataFrame, split: str, file_path: str):
        self.__split = split
        self.df = df
        self.trained_df = None
        self.department = None
        self.__file_path = file_path

    def fit(self):
        self.trained_df = self.df[self.df["split"] == self.__split]
        biggest_department = self.trained_df["department"].value_counts().idxmax()
        print(f"Fitted department: {biggest_department}")
        self.department = biggest_department

    def predict(self, body: str):
        if body is None or body == "":
            print("Body cannot be None or empty")
            return None
        return self.department

    def save(self):
        with open(self.__file_path, "wb") as f:
            pickle.dump(
                {"department": self.department, "trained_df": self.trained_df},
                f,
            )

    @classmethod
    def load(cls, file_path: str):
        # Skip __init__, which requires the full dataframe used by fit().
        model = cls.__new__(cls)
        with open(file_path, "rb") as f:
            payload = pickle.load(f)
        model.department = payload["department"]
        model.trained_df = payload["trained_df"]
        model.__file_path = file_path
        model.df = None
        model.__split = None
        return model
