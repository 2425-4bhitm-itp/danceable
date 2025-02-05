import pytest
import os
import json
from flask import Flask
from app import app  # Assuming your Flask app is in spectrogram_api.py

test_wav_file = "test.wav"
test_spectrogram_dir = "/app/song-storage/spectrogram"
test_spectrogram_file = os.path.join(test_spectrogram_dir, "test_spectrogram.png")

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["message"] == "Service is running"
