import requests
res = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen3.5:4b",
    "prompt": "你是谁",
    "stream": False
})
print(res.json()["response"])