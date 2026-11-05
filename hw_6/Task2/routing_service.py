import importlib.util
import math
from pathlib import Path

DEPARTMENTS = (
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
)

class RoutingService:
    def __init__(self, model_path):
        self._classifier = self.__classifier_class().load(model_path)

    def __classifier_class(self):
        root = Path(__file__).resolve().parents[2]
        path = root / "shared" / "classes" / "ticket_routing_classifier.py"
        spec = importlib.util.spec_from_file_location("ticket_routing_classifier", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("routing classifier could not be loaded")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.TicketRoutingClassifier

    def __body(self,request):
        if not isinstance(request, dict) or "body" not in request:
            raise ValueError("routing request must include body")
        body = request["body"]
        if not isinstance(body, str) or not body.strip():
            raise ValueError("routing body must contain text")
        return body

    def __check(self,result):
        department = result.get("recommended_department")
        scores = result.get("class_scores")
        if department not in DEPARTMENTS or not isinstance(scores, dict):
            raise RuntimeError("routing response is missing required fields")
        if set(scores) != set(DEPARTMENTS):
            raise RuntimeError("routing scores must cover every department")
        if any(isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) for score in scores.values()):
            raise RuntimeError("routing scores must be finite numbers")
        if max(scores, key=lambda name: scores[name]) != department:
            raise RuntimeError("recommended department is not the top score")
        return {"recommended_department": department, "class_scores": scores}

    def route_ticket(self, request):
        body = self.__body(request)
        try:
            result = self._classifier.predict(body)
        except Exception as exc:
            raise RuntimeError("routing classifier failed") from exc
        return self.__check(result)