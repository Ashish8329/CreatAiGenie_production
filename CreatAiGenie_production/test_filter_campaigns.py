import requests
import json

url = "http://127.0.0.1:8000/filter_campaigns/"
headers = {
    "Content-Type": "application/json"
}
data = {
    "main_operator": "AND",
    "conditions": [
        {
            "operator": "OR",
            "filters": {
                "clicks": {
                    "min": 10,
                    "max": 50
                }
            }
        },
        {
            "operator": "AND",
            "filters": {
                "cpc": {
                    "max": 1.5
                }
            }
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())