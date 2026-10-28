def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user_and_get_profile(client):
    response = client.post("/api/v1/ai-vet/users/create", json={"user_id": 42})
    assert response.status_code == 200
    assert response.json() == {"status": "created", "user_id": "42"}

    profile = client.get("/api/v1/ai-vet/users/42")
    assert profile.status_code == 200
    assert profile.json() == {"user_id": "42", "role": "", "animal": ""}


def test_get_unknown_user_returns_404(client):
    response = client.get("/api/v1/ai-vet/users/unknown")
    assert response.status_code == 404


def test_update_user_role_and_animal(client):
    client.post("/api/v1/ai-vet/users/create", json={"user_id": "7"})

    response = client.patch("/api/v1/ai-vet/users/7", json={"role": "Ветеринар", "animal": "Свиньи"})
    assert response.status_code == 200

    profile = client.get("/api/v1/ai-vet/users/7").json()
    assert profile["role"] == "Ветеринар"
    assert profile["animal"] == "Свиньи"


def test_update_unknown_user_returns_404(client):
    response = client.patch("/api/v1/ai-vet/users/nobody", json={"role": "Ветеринар"})
    assert response.status_code == 404


def test_legacy_endpoints_used_by_bot(client):
    client.post("/api/v1/ai-vet/create_user", json={"user_id": "5"})
    client.post("/api/v1/ai-vet/set_user_role", json={"user_id": "5", "role": "Зоотехник"})
    client.post("/api/v1/ai-vet/set_user_animal", json={"user_id": "5", "animal": "Птица"})

    profile = client.get("/api/v1/ai-vet/users/5").json()
    assert profile == {"user_id": "5", "role": "Зоотехник", "animal": "Птица"}
