import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.user import User
from app.models.character import Character
from app.models.conversation import (
    Conversation,
    Message,
    ConversationStatus,
    SenderType,
    ContentType,
)
from app.core.security import get_password_hash


client = TestClient(app)


def test_create_conversation(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试创建会话"""
    data = {
        "character_id": str(test_character.id),
        "title": "测试会话",
        "description": "这是一个测试会话",
        "settings": {"temperature": 0.7, "max_tokens": 1000, "voice_enabled": False},
    }

    response = client.post("/api/v1/conversations/", json=data)
    assert response.status_code == 201

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "测试会话"
    assert data["data"]["character_id"] == str(test_character.id)
    assert data["data"]["status"] == "active"


def test_get_conversations(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试获取会话列表"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话1",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    response = client.get("/api/v1/conversations/")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["conversations"]) == 1
    assert data["data"]["conversations"][0]["title"] == "测试会话1"


def test_get_conversation(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试获取会话详情"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    response = client.get(f"/api/v1/conversations/{conversation.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "测试会话"
    assert data["data"]["character"]["name"] == test_character.name


def test_update_conversation(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试更新会话"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="原始标题",
        description="原始描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    update_data = {
        "title": "更新后的标题",
        "description": "更新后的描述",
        "status": "paused",
    }

    response = client.put(f"/api/v1/conversations/{conversation.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "更新后的标题"
    assert data["data"]["status"] == "paused"


def test_delete_conversation(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试删除会话"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    response = client.delete(f"/api/v1/conversations/{conversation.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "测试会话"


def test_create_message(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试发送消息"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    message_data = {
        "content": "你好，这是一个测试消息",
        "content_type": "text",
        "sender_type": "user",
    }

    response = client.post(
        f"/api/v1/conversations/{conversation.id}/messages", json=message_data
    )
    assert response.status_code == 201

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["content"] == "你好，这是一个测试消息"
    assert data["data"]["sender_type"] == "user"


def test_get_messages(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试获取消息列表"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # 创建测试消息
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        sender_type=SenderType.USER,
        sender_id=normal_user.id,
        content="测试消息内容",
        content_type=ContentType.TEXT,
        status="sent",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    response = client.get(f"/api/v1/conversations/{conversation.id}/messages")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["messages"]) == 1
    assert data["data"]["messages"][0]["content"] == "测试消息内容"


def test_search_conversations(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试搜索会话"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="哲学讨论",
        description="关于哲学的深度讨论",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    search_data = {"query": "哲学", "skip": 0, "limit": 10}

    response = client.post("/api/v1/conversations/search", json=search_data)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["conversations"]) == 1
    assert "哲学" in data["data"]["conversations"][0]["title"]


def test_search_messages(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试搜索消息"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # 创建测试消息
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        sender_type=SenderType.USER,
        sender_id=normal_user.id,
        content="这是一个关于AI的讨论",
        content_type=ContentType.TEXT,
        status="sent",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    search_data = {"query": "AI", "skip": 0, "limit": 10}

    response = client.post(
        f"/api/v1/conversations/{conversation.id}/messages/search", json=search_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["results"]) == 1
    assert "AI" in data["data"]["results"][0]["content"]


def test_get_conversation_stats(
    db: Session, normal_user: User, test_character: Character
) -> None:
    """测试获取会话统计"""
    # 创建测试会话
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=normal_user.id,
        character_id=test_character.id,
        title="测试会话",
        description="测试描述",
        status=ConversationStatus.ACTIVE,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # 创建测试消息
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        sender_type=SenderType.USER,
        sender_id=normal_user.id,
        content="测试消息",
        content_type=ContentType.TEXT,
        status="sent",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    response = client.get(f"/api/v1/conversations/{conversation.id}/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["data"]["stats"]["total_messages"] == 1
    assert data["data"]["stats"]["user_messages"] == 1


def test_unauthorized_access() -> None:
    """测试未授权访问"""
    response = client.get("/api/v1/conversations/")
    assert response.status_code == 401


def test_conversation_not_found(db: Session, normal_user: User) -> None:
    """测试会话不存在"""
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/conversations/{fake_id}")
    assert response.status_code == 404
