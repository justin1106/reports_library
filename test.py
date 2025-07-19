import requests

url = "http://192.168.1.18:6333/collections/cu_reports/points/count"
response = requests.post(url, json={"filter": None})
print(response.json())
