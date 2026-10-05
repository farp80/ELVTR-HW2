import pandas as pd


class PandasUtils:
    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        self.settings = {}
        self.df = self.read_csv()

    def read_csv(self):
        return pd.read_csv(self.__kwargs["file_path"])

    def get_settings(self, column: str):
        self.settings[column] = {}

        print(f"Value counts: {self.df[column].value_counts()}")
        print(f"Head: {self.df[column].head(10).tolist()}")
        print(f"Isna: {self.df[column].isna().sum()}")
        print(f"Unique: {self.df[column].unique()}")
        print(f"Dtype: {self.df[column].dtype}")
        print(f"Describe: {self.df[column].describe()}")
        print(f"Info: {self.df[column].info()}")
        print(f"Head: {self.df[column].head(10).tolist()}")
        print(f"Tail: {self.df[column].tail(10).tolist()}")
        print(f"Sample: {self.df[column].sample(10).tolist()}")
        print(f"Duplicated: {self.df[column].duplicated(keep=False)}")
        print(self.df[column].isna().sum())

        if column == "ticket_id":
            print(f"Invalid ticket: {self.df[column] <= 0}")
            self.settings[column]["invalid"] = (self.df[column] <= 0).sum()

            print(f"Minimum ticket: {self.df[column].min()}")
            self.settings[column]["minimum"] = self.df[column].min()

            print(f"Maximum ticket: {self.df[column].max()}")
            self.settings[column]["maximum"] = self.df[column].max()

            print(f"Number of Unique IDs: {self.df[column].nunique()}")

        self.settings[column] = {
            "value_counts": self.df[column].value_counts(),
            "head": self.df[column].head(10).tolist(),
            "isna": self.df[column].isna().sum(),
            "unique": self.df[column].unique(),
            "dtype": self.df[column].dtype,
            "describe": self.df[column].describe(),
            "info": self.df[column].info(),
            "duplicated": self.df[column].duplicated(keep=False).sum(),
        }

    def create_dataframe(self, data, columns=None):
        return pd.DataFrame(data, columns=columns)

    def column_standarization(self):
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(" ", "_")
        return self.df.columns.tolist()

    @staticmethod
    def evaluate_keyword(trained_df, department, keyword1, keyword2):
        matches = trained_df["body"].str.lower().str.contains(
            keyword1.lower(), regex=False, na=False
        ) & (
            trained_df["body"]
            .str.lower()
            .str.contains(keyword2.lower(), regex=False, na=False)
        )

        in_class = (matches & (trained_df["department"] == department)).sum()
        out_of_class = (matches & (trained_df["department"] != department)).sum()
        return {
            "in_class": in_class,
            "out_of_class": out_of_class,
        }
