from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get('/upload/')
print('status', response.status_code)
print('body', response.text)