import pytest
from pydantic import ValidationError
from backend.shared.src.schemas.ai_companion_schema import AICompanionCreate, AICompanionUpdate

def test_ai_companion_create_valid():
    """Test a valid AICompanionCreate schema."""
    data = {
        "name": "Luna",
        "description": "A creative companion",
        "personality": {"trait": "creative"}
    }
    companion = AICompanionCreate(**data)
    assert companion.name == "Luna"
    assert companion.personality["trait"] == "creative"

def test_ai_companion_create_name_required():
    """Test that 'name' is required in AICompanionCreate."""
    with pytest.raises(ValidationError):
        AICompanionCreate(description="Missing name")

def test_ai_companion_update_partial():
    """Test that AICompanionUpdate allows partial updates."""
    data = {"description": "An updated description"}
    update = AICompanionUpdate(**data)
    assert update.description == "An updated description"
    assert update.name is None
