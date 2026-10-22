class ClassificationMetricEvaluator:
    def __init__(self, prediction_df) -> None:
        self.df = prediction_df
        self.df["true_label_clean"] = self.df["true_label"].apply(self.normalize_label)
        self.df["pred_label_clean"] = self.df["recommended_department"].apply(
            self.normalize_label
        )
        self.labels = sorted(
            set(self.df["true_label_clean"]) | set(self.df["pred_label_clean"])
        )

    def normalize_label(self, label):
        return str(label).strip().lower()

    def accuracy(self, df=None):
        data = self.df if df is None else df

        correct = (data["true_label_clean"] == data["pred_label_clean"]).sum()
        total = len(data)

        return 0 if total == 0 else correct / total

    def multiclass_confusion_matrix(self, df=None):
        data = self.df if df is None else df

        matrix = {}

        for true_label in self.labels:
            matrix[true_label] = {}

            for pred_label in self.labels:
                count = (
                    (data["true_label_clean"] == true_label)
                    & (data["pred_label_clean"] == pred_label)
                ).sum()

                matrix[true_label][pred_label] = int(count)

        return matrix

    def fundamental_outcomes(self, label, df=None):
        # fp: actual department and predicted department match the label
        # fp: predicted as the label, but actual is different
        # fn: actual is the label, but predicted is different
        # tn: actual is not the label and predicted is not the label

        data = self.df if df is None else df

        is_actual_label = data["true_label_clean"] == label
        is_predicted_label = data["pred_label_clean"] == label

        tp = (is_actual_label & is_predicted_label).sum()
        fp = (~is_actual_label & is_predicted_label).sum()
        fn = (is_actual_label & ~is_predicted_label).sum()
        tn = (~is_actual_label & ~is_predicted_label).sum()

        return {
            "label": label,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
        }

    def precision_recall_f1(self, label, df=None):
        counts = self.fundamental_outcomes(label, df)

        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]

        precision = 0 if tp + fp == 0 else tp / (tp + fp)
        recall = 0 if tp + fn == 0 else tp / (tp + fn)
        f1 = (
            0
            if precision + recall == 0
            else 2 * precision * recall / (precision + recall)
        )

        support = tp + fn

        return {
            "label": label,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": int(support),
            "tp": counts["tp"],
            "fp": counts["fp"],
            "fn": counts["fn"],
            "tn": counts["tn"],
        }

    def per_class_metrics(self, df=None):
        rows = [self.precision_recall_f1(label, df) for label in self.labels]

        return rows

    def macro_f1(self, df=None):
        # primary metric
        per_class = self.per_class_metrics(df)
        class_length = len(per_class)

        if class_length == 0:
            return 0

        total_f1 = sum(row["f1"] for row in per_class)
        return total_f1 / class_length

    def weighted_f1(self, df=None):
        # secondary metric
        per_class = self.per_class_metrics(df)
        total_support = sum(row["support"] for row in per_class)

        if total_support == 0:
            return 0

        weighted_total = 0

        for row in per_class:
            weighted_total += row["f1"] * row["support"]

        return weighted_total / total_support

    def summary_metrics(self, df=None):
        return {
            "accuracy": float(self.accuracy(df)),
            "macro_f1": self.macro_f1(df),
            "weighted_f1": self.weighted_f1(df),
        }

    def length_cutoffs(self, lengths):
        # we are using third for the slicing.
        short_cutoff = lengths.quantile(0.33)
        medium_cutoff = lengths.quantile(0.66)
        return short_cutoff, medium_cutoff

    def length_slice(self, length, short_cutoff, medium_cutoff):
        if length <= short_cutoff:
            return "short"
        if length <= medium_cutoff:
            return "medium"
        return "long"

    def add_body_length_slices(self, body_df):
        merged = self.df.merge(
            body_df[["ticket_id", "body"]], on="ticket_id", how="left"
        )
        merged["body_length"] = merged["body"].fillna("").astype(str).str.len()
        short_cutoff, medium_cutoff = self.length_cutoffs(merged["body_length"])
        merged["body_length_slice"] = merged["body_length"].apply(
            lambda length: self.length_slice(length, short_cutoff, medium_cutoff)
        )
        self.df = merged

        return self.df

    def metrics_by_slice(self):
        results = {}

        for slice_name in ["short", "medium", "long"]:
            slice_df = self.df[self.df["body_length_slice"] == slice_name]
            results[slice_name] = {
                "row_count": len(slice_df),
                "summary": self.summary_metrics(slice_df),
                "per_class": self.per_class_metrics(slice_df),
            }

        return results
