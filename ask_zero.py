import requests

def ask_zero(question):
    """שאל את Zero משהו"""
    response = requests.post('http://localhost:8080/api/chat', 
        json={"message": question}
    )
    return response.json()['response']

# דוגמה:
answer = ask_zero("מה זה machine learning?")
print(answer)