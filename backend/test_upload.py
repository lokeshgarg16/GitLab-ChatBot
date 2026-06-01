from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path

p = Path('test_upload.txt')
p.write_text('Hello world\nThis is a test.', encoding='utf-8')
client = TestClient(app)
with p.open('rb') as f:
    response = client.post('/upload/', files={'file': ('test_upload.txt', f, 'text/plain')})
print('status', response.status_code)
print('body', response.text)
