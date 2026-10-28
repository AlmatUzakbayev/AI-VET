UPLOAD_URL = "/api/v1/ai-vet/documents/upload"
TEXT = "У коровы диарея второй день. Температура в норме. Аппетит снижен."


def test_upload_txt_document(client, vector_store, tmp_path):
    response = client.post(UPLOAD_URL, files={"file": ("notes.txt", TEXT.encode(), "text/plain")})

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "notes.txt"
    assert body["chunk_count"] == 1
    assert body["summary"] == "краткое содержание"
    assert (tmp_path / "0_notes.txt").exists()

    document_id, chunks = vector_store.upserted[0]
    assert document_id == 1
    assert TEXT in chunks[0]["text"]


def test_upload_filename_cannot_escape_uploads_directory(client, tmp_path):
    response = client.post(
        UPLOAD_URL,
        params={"user_id": "../../hack"},
        files={"file": ("../../evil.txt", TEXT.encode(), "text/plain")},
    )

    assert response.status_code == 200
    assert [p.name for p in tmp_path.iterdir()] == ["hack_evil.txt"]
    assert not (tmp_path.parent / "evil.txt").exists()
    assert not (tmp_path.parent.parent / "evil.txt").exists()


def test_upload_unsupported_extension_returns_400(client, vector_store):
    response = client.post(UPLOAD_URL, files={"file": ("virus.exe", b"MZ", "application/octet-stream")})

    assert response.status_code == 400
    assert vector_store.upserted == []


def test_upload_too_large_file_returns_400_with_real_limit(client, vector_store):
    content = b"a" * (10 * 1024 * 1024 + 1)

    response = client.post(UPLOAD_URL, files={"file": ("big.txt", content, "text/plain")})

    assert response.status_code == 400
    assert "10MB" in response.json()["detail"]
    assert vector_store.upserted == []


def test_upload_empty_document_returns_400(client, vector_store):
    response = client.post(UPLOAD_URL, files={"file": ("empty.txt", b"", "text/plain")})

    assert response.status_code == 400
    assert vector_store.upserted == []


def test_delete_document(client, vector_store):
    response = client.delete("/api/v1/ai-vet/documents/5")

    assert response.status_code == 200
    assert response.json() == {"status": "deleted", "id": 5}
    assert vector_store.deleted == [5]


def test_delete_document_with_non_numeric_id_returns_422(client, vector_store):
    response = client.delete("/api/v1/ai-vet/documents/abc")

    assert response.status_code == 422
    assert vector_store.deleted == []
