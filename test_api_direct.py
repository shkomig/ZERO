#!/usr/bin/env python3
"""
Test the API directly to see which model it uses
"""

import requests
import json

# Test Hebrew question
hebrew_question = "שלום, איך אתה היום?"
response = requests.post('http://localhost:8080/api/chat', 
    json={"message": hebrew_question})
print(f"Hebrew question: {hebrew_question}")
print(f"Response: {response.json()}")

# Test English question
english_question = "Hello, how are you today?"
response = requests.post('http://localhost:8080/api/chat', 
    json={"message": english_question})
print(f"\nEnglish question: {english_question}")
print(f"Response: {response.json()}")

