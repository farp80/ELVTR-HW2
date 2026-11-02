# Routing service contract

## Request

`route_ticket` takes one dictionary. The required field is `body`, a string. After `strip()`, at least one character must remain. That string is the ticket `Body` with the same characters the caller sent.

## Response

The method returns one dictionary with two fields. `recommended_department` is one of the ten Homework 4 department names. `class_scores` is an object whose keys are exactly those ten names. Each value is a finite number. The key with the highest value is `recommended_department`.

## Errors

A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The classifier is not called.

If the saved model fails, or the prediction breaks a response rule above, the method raises `RuntimeError`.
