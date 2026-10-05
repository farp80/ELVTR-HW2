class Logs:
    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        self.logs = []

    def log_decision(
        self,
        issue,
        action,
        reason,
        affected_count,
        representative_ids,
        risk_or_limitation,
    ):
        self.logs.append(
            {
                "issue": issue,
                "action": action,
                "reason": reason,
                "affected_count": affected_count,
                "representative_ids": representative_ids,
                "risk_or_limitation": risk_or_limitation,
            }
        )
