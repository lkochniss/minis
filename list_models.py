from google import genai
import os

# Assuming the client is configured via environment variables (standard for google-genai)
client = genai.Client()
models = client.models.list()
for model in models:
    print(model.name)
