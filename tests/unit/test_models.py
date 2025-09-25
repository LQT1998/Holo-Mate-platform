import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Import all models and Base
from backend.shared.src.models.base import Base
from backend.shared.src.models.user import User
from backend.shared.src.models.ai_companion import AICompanion
from backend.shared.src.models.conversation import Conversation
from backend.shared.src.models.message import Message
from backend.shared.src.models.hologram_device import HologramDevice
from backend.shared.src.models.character_asset import CharacterAsset
from backend.shared.src.models.subscription import Subscription
from backend.shared.src.models.user_preference import UserPreference
from backend.shared.src.models.voice_profile import VoiceProfile
from backend.shared.src.models.animation_sequence import AnimationSequence


@pytest.fixture(scope="module")
def session():
    """Fixture to create a temporary in-memory SQLite database session for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(engine)

def test_user_model_creation(session):
    """Test creating a User instance and committing it to the database."""
    email = f"test_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        hashed_password="test_password"
    )
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(email=email).first()
    assert retrieved_user is not None
    assert retrieved_user.email == email
    assert retrieved_user.is_active is True
    assert retrieved_user.id is not None

def test_user_relationships(session):
    """Test the relationships defined on the User model."""
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="test_password")
    
    # Test one-to-one relationships
    user.preferences = UserPreference(language="fr")
    user.subscription = Subscription(plan_name="pro")

    # Test one-to-many relationships
    user.ai_companions.append(AICompanion(name="Companion1"))
    user.devices.append(HologramDevice(name="Device1", device_type="mobile_app"))
    
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).get(user.id)
    assert retrieved_user.preferences.language == "fr"
    assert retrieved_user.subscription.plan_name == "pro"
    assert len(retrieved_user.ai_companions) == 1
    assert retrieved_user.ai_companions[0].name == "Companion1"
    assert len(retrieved_user.devices) == 1
    assert retrieved_user.devices[0].name == "Device1"

def test_ai_companion_model_creation(session):
    """Test creating an AICompanion instance."""
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="test_password")
    session.add(user)
    session.commit()

    companion = AICompanion(
        user_id=user.id,
        name="Test Companion",
        personality={"trait": "friendly"}
    )
    session.add(companion)
    session.commit()

    retrieved_companion = session.query(AICompanion).get(companion.id)
    assert retrieved_companion is not None
    assert retrieved_companion.name == "Test Companion"
    assert retrieved_companion.user_id == user.id
    assert retrieved_companion.personality["trait"] == "friendly"

def test_conversation_and_message_models(session):
    """Test creating Conversation and Message instances and their relationship."""
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="test_password")
    companion = AICompanion(name="Test Companion", user=user)
    session.add(user)
    session.add(companion)
    session.commit()

    conversation = Conversation(
        user_id=user.id,
        ai_companion_id=companion.id,
        title="First Chat"
    )
    session.add(conversation)
    session.commit()

    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello!"
    )
    session.add(message)
    session.commit()

    retrieved_conversation = session.query(Conversation).get(conversation.id)
    assert len(retrieved_conversation.messages) == 1
    assert retrieved_conversation.messages[0].content == "Hello!"
    assert retrieved_conversation.messages[0].role == "user"

def test_device_model_creation(session):
    """Test creating a HologramDevice instance."""
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="test_password")
    session.add(user)
    session.commit()

    device = HologramDevice(
        user_id=user.id,
        name="Living Room Holo-Fan",
        device_type="hologram_fan",
        serial_number=str(uuid.uuid4())
    )
    session.add(device)
    session.commit()

    retrieved_device = session.query(HologramDevice).get(device.id)
    assert retrieved_device is not None
    assert retrieved_device.name == "Living Room Holo-Fan"
    assert retrieved_device.status == "offline"

def test_asset_and_animation_models(session):
    """Test CharacterAsset and AnimationSequence models and their relationship."""
    user = User(email=f"test_{uuid.uuid4()}@example.com", hashed_password="test_password")
    companion = AICompanion(name="Asset Companion", user=user)
    session.add_all([user, companion])
    session.commit()

    asset = CharacterAsset(
        ai_companion_id=companion.id,
        model_url="http://example.com/model.glb"
    )
    session.add(asset)
    session.commit()

    animation = AnimationSequence(
        character_asset_id=asset.id,
        trigger_event="on_greeting",
        animation_url="http://example.com/greet.anim"
    )
    session.add(animation)
    session.commit()

    retrieved_asset = session.query(CharacterAsset).get(asset.id)
    assert len(retrieved_asset.animations) == 1
    assert retrieved_asset.animations[0].trigger_event == "on_greeting"
    assert retrieved_asset.ai_companion_id == companion.id

def test_full_relationship_cascade(session):
    """Test a full user deletion cascade to ensure all related data is removed."""
    # 1. Create a user with all related objects
    user = User(email=f"test_cascade_{uuid.uuid4()}@example.com", hashed_password="password")
    user.preferences = UserPreference()
    user.subscription = Subscription(plan_name="premium")
    user.devices.append(HologramDevice(name="Test Device", device_type="hologram_fan", serial_number=str(uuid.uuid4())))
    
    companion = AICompanion(name="Cascade Companion")
    user.ai_companions.append(companion)
    
    asset = CharacterAsset(model_url="url")
    companion.character_asset = asset
    
    animation = AnimationSequence(trigger_event="wave", animation_url="url")
    asset.animations.append(animation)
    
    companion.voice_profile = VoiceProfile(provider_voice_id="voice123")
    
    conversation = Conversation(title="Cascade Chat")
    companion.conversations.append(conversation)
    user.conversations.append(conversation)
    
    message = Message(role="user", content="Cascade message")
    conversation.messages.append(message)
    
    session.add(user)
    session.commit()
    
    user_id = user.id

    # 2. Delete the user
    session.delete(user)
    session.flush()  # Ensure cascade operations are processed
    session.commit()

    # 3. Verify that all related data is gone
    assert session.query(User).get(user_id) is None
    assert session.query(UserPreference).filter_by(user_id=user_id).count() == 0
    assert session.query(Subscription).filter_by(user_id=user_id).count() == 0
    assert session.query(HologramDevice).filter_by(user_id=user_id).count() == 0
    assert session.query(AICompanion).filter_by(user_id=user_id).count() == 0
    # The rest should be cascaded from AICompanion and Conversation deletions
    assert session.query(Conversation).count() == 0
    assert session.query(Message).count() == 0
    assert session.query(CharacterAsset).count() == 0
    assert session.query(AnimationSequence).count() == 0
    assert session.query(VoiceProfile).count() == 0
