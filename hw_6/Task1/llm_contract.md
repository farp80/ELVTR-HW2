# LLM service contract

## Request

`call_llm` takes one dictionary.

`messages` is a list with at least one object. Each object has a string `role` and a string `content`.

`model` is a non-empty string. It is the Ollama model name for this call.

`options` is an object. It holds the generation settings for this call, such as temperature, seed, and `num_predict`.

`schema` is optional. When the caller sends it, it is an object that describes the output shape. When the caller omits it, this call has no fixed shape.

The service stores the Ollama URL. The caller sends the prompt, the model, the settings, and the schema on every call.

## Response

The method returns one dictionary with the field `content`. The value is the raw text from Ollama. Parsing that text is the caller's job.

## Errors

A request that breaks a rule above raises `ValueError`. Ollama is not called.

If Ollama cannot be reached, the HTTP call fails, or the reply has no text, the method raises `RuntimeError`.
