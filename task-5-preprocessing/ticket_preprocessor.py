import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class TicketPreprocessor:
    def __init__(self, cleaned_df, splitted_df):
        self.__cleaned_df = cleaned_df
        self.__splitted_df = splitted_df
        self.__df = None
        self.__x_train = None
        self.__y_train = None
        self.__x_validation = None
        self.__y_validation = None
        self.__x_test = None
        self.__y_test = None

        # min_df: removes terms occurring in only one document.
        # max_df: removes features appearing in more than 95% of documents..
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )

    def load(self):
        """ Loads the data and merges the cleaned and splitted dataframes. """
        self.__df = self.__cleaned_df.merge(
            self.__splitted_df, on="ticket_id", how="inner"
        )

        return self.__df

    def split(self):
        """ Splits the data into train, validation and test sets. """
        train_df = self.__df[self.__df["split"] == "train"].copy()
        validation_df = self.__df[self.__df["split"] == "validation"].copy()
        test_df = self.__df[self.__df["split"] == "test"].copy()

        # select modeling fields: body and department
        self.__x_train = train_df["body"]
        self.__y_train = train_df["department"]
        self.__x_validation = validation_df["body"]
        self.__y_validation = validation_df["department"]
        self.__x_test = test_df["body"]
        self.__y_test = test_df["department"]

        return (
            self.__x_train,
            self.__y_train,
            self.__x_validation,
            self.__y_validation,
            self.__x_test,
            self.__y_test,
        )

    def fit_transform(self):
        """ Fits the vectorizer and transforms the data. """
        return self.vectorizer.fit_transform(self._prepare_texts(self.__x_train))

    def transform(self, x):
        """ Transforms the data using the vectorizer. """
        return self.vectorizer.transform(self._prepare_texts(x))

    @staticmethod
    def _prepare_texts(x):
        """Returns an iterable of text documents for the vectorizer."""
        if isinstance(x, str):
            return [x]

        if isinstance(x, pd.Series):
            return x.fillna("").astype(str)

        return pd.Series(x).fillna("").astype(str)