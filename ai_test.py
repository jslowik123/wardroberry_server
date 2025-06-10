import base64
import requests

url = "http://localhost:8000/extract-clothing-image"

file = open("test_2.jpg", "rb")

response = requests.post(url, files={"file": file})

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {response.headers}")
print(f"Response Text: '{response.text}'")
print(f"Response Length: {len(response.text)}")

if response.status_code == 200:
    try:
        print("JSON Response:", response.json())
    except Exception as e:
        print(f"JSON Parse Error: {e}")
else:
    print("HTTP Error - Server returned non-200 status")