import pytest
import whisper
import json

from src import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    return app.test_client()


def test_detect_options(client):
    response = client.options('/v1/detect')

    assert response.status_code == 200
    assert response.get_json() == {
        "queryParams": {
            "model": {
                "type": "enum",
                "options": whisper.available_models(),
                "optional": True,
                "default": "tiny",
            },
        }
    }


def test_transcribe_options(client):
    response = client.options('/v1/transcribe')

    assert response.status_code == 200
    assert response.get_json() == {
        "queryParams": {
            "model": {
                "type": "enum",
                "options": whisper.available_models(),
                "optional": True,
                "default": "tiny",
            },
            "task": {
                "type": "enum",
                "options": ["translate", "transcribe"],
                "optional": True,
                "default": "transcribe",
            },
            "languages": {
                "type": "enum",
                "options": list(whisper.tokenizer.LANGUAGES.values()),
                "optional": True,
            },
            "email_callback": {
                "type": "string",
                "optional": False,
            },
            "filename": {
                "type": "string",
                "optional": True,
                "default": "untitled-transcription"
            },
        }
    }


def test_download_options(client):
    response = client.options('/v1/download/abc123')

    assert response.status_code == 200
    assert response.get_json() == {
        "queryParams": {
            "output": {
                "type": "enum",
                "options": ["srt", "vtt", "json", "txt", "timecode_txt"],
                "optional": True,
                "default": "srt",
            },
        }
    }


def test_download_not_found(client):
    response = client.get('/v1/download/1')

    assert response.status_code == 404


def test_transcribe_enqueue(client):
    with open('tests/test.mp3', 'rb') as f:
        data = f.read()

    response = client.post(
        '/v1/transcribe?model=tiny&task=transcribe&languages=english&email_callback=example@example.com',  data=data, content_type='audio/mp3')

    assert response.status_code == 201

    response_data = json.loads(response.data)
    assert 'job_id' in response_data and bool(response_data['job_id'])


def test_detect_language(client):
    with open('tests/test.mp3', 'rb') as f:
        data = f.read()

    response = client.post('/v1/detect?model=tiny',
                           data=data, content_type='audio/mp3')

    assert response.status_code == 200
    assert response.get_json() == {
        'detectedLanguage': 'english', 'languageCode': 'en'}


def test_queue(client):
    with open('tests/test.mp3', 'rb') as f:
        data = f.read()

    client.post('/v1/transcribe?model=tiny&task=transcribe&languages=english&email_callback=example@example.com',
                data=data, content_type='audio/mp3')

    response = client.get('/v1/queue',  data=data, content_type='audio/mp3')

    assert response.status_code == 200

    response_data = json.loads(response.data)
    assert 'count' in response_data and response_data['count'] > 0
