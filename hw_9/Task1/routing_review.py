def review_decision(class_scores):
    ordered = sorted(class_scores.values(), reverse=True)
    margin = round(ordered[0] - ordered[1], 4)
    return margin < 0.05, margin