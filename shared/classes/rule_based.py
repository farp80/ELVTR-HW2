import pickle


class RuleBasedBaseline:
    def __init__(self, majority_department, rules):
        self.majority_department = majority_department
        self.rules = sorted(
            rules,
            key=lambda rule: (-rule["precision"], rule["phrase"]),
        )

    def predict(self, body):
        text = "" if body is None else str(body).lower()
        for rule in self.rules:
            if rule["phrase"] in text:
                return rule["department"]
        return self.majority_department

    def save(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(
                {
                    "majority_department": self.majority_department,
                    "rules": self.rules,
                },
                file,
            )

    @classmethod
    def load(cls, file_path):
        with open(file_path, "rb") as file:
            payload = pickle.load(file)
        return cls(payload["majority_department"], payload["rules"])
