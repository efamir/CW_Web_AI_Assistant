import pytest
from unittest.mock import patch, ANY
from io import BytesIO
from db import User, Role, Note


def test_api_register_and_login(test_client, db_s):
    # Реєстрація
    reg_payload = {"username": "api_user1", "password": "mypassword"}
    reg_resp = test_client.post("/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert "token" in reg_data and reg_data["token"]
    user_api_token = reg_data["token"]

    # Вхід
    login_payload = {"username": "api_user1", "password": "mypassword"}
    login_resp = test_client.post("/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    assert login_data["token"] == user_api_token

def test_api_login_bad_password(test_client, db_s):
    # Реєструємо користувача
    test_client.post("/register", json={"username": "login_fail_user", "password": "good_pass"})

    # Спроба входу з неправильним паролем
    login_resp = test_client.post("/login", json={"username": "login_fail_user", "password": "bad_pass"})
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is False
    assert login_data["error"] == "password"


def test_api_create_and_get_user_notes(test_client, db_s):
    # Реєстрація та вхід для отримання токена
    test_client.post("/register", json={"username": "notes_api_user", "password": "pass"})
    login_resp = test_client.post("/login", json={"username": "notes_api_user", "password": "pass"})
    my_token = login_resp.json()["token"]

    # Створення нотатки
    note_payload = {"token": my_token, "text": "Нотатка через API!"}
    create_resp = test_client.post("/create_note", json=note_payload)
    assert create_resp.status_code == 200
    created_note_data = create_resp.json()
    assert created_note_data["text"] == "Нотатка через API!"
    assert "id" in created_note_data

    # Отримання списку нотаток
    notes_list_resp = test_client.post("/notes", json={"token": my_token})
    assert notes_list_resp.status_code == 200
    notes_data = notes_list_resp.json()
    assert isinstance(notes_data, list)
    assert len(notes_data) == 1
    assert notes_data[0]["text"] == "Нотатка через API!"


@patch('app.handler.process_prompt') # Імітуємо handler в app.py
def test_api_process_text_prompt(mock_app_handler_text_proc, test_client, db_s):
    test_client.post("/register", json={"username": "api_text_user", "password": "pass"})
    login_resp = test_client.post("/login", json={"username": "api_text_user", "password": "pass"})
    my_token = login_resp.json()["token"]

    mock_app_handler_text_proc.return_value = {
        "response_text": "API відповіло на текст",
        "audio_file_path": "static/api_audio_reply.wav",
        "timer_timestamp": None
    }

    with patch('app.os.remove'):
        api_resp = test_client.post("/process_text", json={
            "token": my_token,
            "prompt": "Тест для API тексту"
        })

    assert api_resp.status_code == 200
    resp_data = api_resp.json()
    assert resp_data["response_text"] == "API відповіло на текст"
    assert resp_data["audio_file_path"] == "static/api_audio_reply.wav"

    user = db_s.query(User).filter_by(token=my_token).first()
    assert user is not None
    mock_app_handler_text_proc.assert_called_once_with(user.id, "Тест для API тексту")

@patch('app.handler.process_prompt_by_audio_file')
def test_api_process_audio_prompt(mock_app_handler_audio_proc, test_client, db_s):
    test_client.post("/register", json={"username": "api_audio_user", "password": "pass"})
    login_resp = test_client.post("/login", json={"username": "api_audio_user", "password": "pass"})
    my_token = login_resp.json()["token"]

    mock_app_handler_audio_proc.return_value = {
        "response_text": "API відповіло на аудіо",
        "audio_file_path": "static/api_audio_from_audio.wav",
        "timer_timestamp": 98765
    }

    dummy_audio_bytes = BytesIO(b"some audio data for upload")
    upload_files = {'file': ('test_audio.mp3', dummy_audio_bytes, 'audio/mpeg')}

    with patch('app.os.remove'):
        api_resp = test_client.post(
            "/process_audio",
            data={"token": my_token},
            files=upload_files
        )

    assert api_resp.status_code == 200
    resp_data = api_resp.json()
    assert resp_data["response_text"] == "API відповіло на аудіо"
    assert resp_data["timer_timestamp"] == 98765

    user = db_s.query(User).filter_by(token=my_token).first()
    assert user is not None
    mock_app_handler_audio_proc.assert_called_once_with(user.id, ANY)

def test_api_get_main_html_page(test_client):
    resp = test_client.get("/main-page")
    assert resp.status_code == 200
    assert "Jarvice" in resp.text
