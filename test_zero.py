import requests

response = requests.post('http://localhost:8080/api/chat', 
    json={"message": "היי זירו, מה המצב?"})

print(response.json()['response'])