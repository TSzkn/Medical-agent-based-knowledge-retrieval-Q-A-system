import requests

def test_generate_api():
    url = "http://36.212.25.245:5110/generate"
    payload = {"text": "新增的国考指标有哪些？"}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        generated_text = data.get("generated_text")
        print("Generated Text:")
        print(generated_text)
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_generate_api()
