from app.auth.security import hash_password, verify_password

from app.database.models import Conversation, Message, User


def test_password_is_hashed():
    password = "testpassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_password_verification_success():
    password = "testpassword123"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


def test_password_verification_failure():
    password = "testpassword123"

    hashed_password = hash_password(password)

    assert not verify_password("wrongpassword", hashed_password)


def test_user_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "integration@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "integration@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_duplicate_user_registration(client):
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email is already registered."


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "wrongpassword123",
        },
    )

    assert response.status_code == 401


def test_get_current_user_with_valid_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "jwt@example.com",
            "password": "testpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "jwt@example.com",
            "password": "testpassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "jwt@example.com"


def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def create_authenticated_user(client, email):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "testpassword123",
        },
    )

    return response.json()["access_token"]


def test_user_cannot_access_another_users_conversation(client, db_session):
    token_a = create_authenticated_user(client, "usera@example.com")
    token_b = create_authenticated_user(client, "userb@example.com")

    # Create a conversation owned by User A
    db = db_session

    user_a = db.query(User).filter_by(email="usera@example.com").first()

    conversation = Conversation(
        title="Private conversation",
        user_id=user_a.id,
    )

    db.add(conversation)
    db.commit()
    conversation_id = conversation.id
    db.close()

    # User B attempts to access it
    response = client.get(
        f"/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404


def test_user_can_access_own_conversation(client, db_session):
    token = create_authenticated_user(client, "owner@example.com")

    db = db_session
    user = db.query(User).filter_by(email="owner@example.com").first()

    conversation = Conversation(
        title="My conversation",
        user_id=user.id,
    )

    db.add(conversation)
    db.commit()
    conversation_id = conversation.id
    db.close()

    response = client.get(
        f"/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "My conversation"


def test_chat_requires_authentication(client):
    response = client.post(
        "/chat",
        json={"question": "What is our company policy?"},
    )

    assert response.status_code == 401


def test_chat_creates_conversation_and_messages(client, monkeypatch, db_session):
    token = create_authenticated_user(client, "chat@example.com")

    # Mock the external RAG/LLM call
    monkeypatch.setattr(
        "app.main.answer_question",
        lambda question, user_id: {
            "answer": "This is a test answer.",
            "sources": [],
        },
    )

    response = client.post(
        "/chat",
        json={"question": "What is our company policy?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "This is a test answer."
    assert data["conversation_id"] is not None

    # Verify conversation and messages were persisted
    db = db_session

    conversation = db.get(Conversation, data["conversation_id"])

    assert conversation is not None
    assert conversation.title == "What is our company policy?"
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == "user"
    assert conversation.messages[1].role == "assistant"

    db.close()


def test_chat_cannot_access_another_users_conversation(client, monkeypatch, db_session):
    token_a = create_authenticated_user(client, "chata@example.com")
    token_b = create_authenticated_user(client, "chatb@example.com")

    db = db_session
    user_a = db.query(User).filter_by(email="chata@example.com").first()

    conversation = Conversation(
        title="Private conversation",
        user_id=user_a.id,
    )

    db.add(conversation)
    db.commit()
    conversation_id = conversation.id
    db.close()

    # This should never need to call the RAG pipeline
    def unexpected_answer(*args, **kwargs):
        raise AssertionError("RAG should not be called for an unauthorized conversation")

    monkeypatch.setattr("app.main.answer_question", unexpected_answer)

    response = client.post(
        "/chat",
        json={
            "question": "Read this conversation",
            "conversation_id": conversation_id,
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404


def test_upload_requires_authentication(client):
    response = client.post(
        "/upload",
        files={
            "file": ("test.pdf", b"fake pdf content", "application/pdf"),
        },
    )

    assert response.status_code == 401
