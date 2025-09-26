"""
Tests for DeviceService
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from streaming_service.src.services.device_service import DeviceService
from shared.src.models.hologram_device import HologramDevice
from shared.src.enums.device_enums import DeviceStatus, DeviceType


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock async database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def device_service(mock_db_session):
    """Fixture to create DeviceService with mock database session."""
    return DeviceService(mock_db_session)


@pytest.fixture
def sample_device_data():
    """Fixture for sample device data."""
    return {
        "serial": "TEST123456",
        "name": "Test Device",
        "device_type": "hologram_fan",
        "device_model": "HoloMate Pro",
        "firmware_version": "1.0.0",
        "hardware_info": {"cpu": "ARM64", "memory": "8GB"}
    }


class TestDeviceServiceRegister:
    """Test cases for device registration"""

    @pytest.mark.asyncio
    async def test_register_device_success(self, device_service, mock_db_session, sample_device_data):
        """Test successful device registration"""
        user_id = uuid4()
        
        # Mock no existing device
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Mock device creation
        mock_device = HologramDevice(
            id=uuid4(),
            user_id=user_id,
            serial_number=sample_device_data["serial"],
            name=sample_device_data["name"],
            device_type=sample_device_data["device_type"],
            status=DeviceStatus.unpaired
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_device.id)
        
        result = await device_service.register_device(
            user_id=user_id,
            serial=sample_device_data["serial"],
            name=sample_device_data["name"],
            device_type=sample_device_data["device_type"],
            device_model=sample_device_data["device_model"],
            firmware_version=sample_device_data["firmware_version"],
            hardware_info=sample_device_data["hardware_info"]
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_device_duplicate_serial(self, device_service, mock_db_session, sample_device_data):
        """Test device registration with duplicate serial number"""
        user_id = uuid4()
        
        # Mock IntegrityError on commit (simulating duplicate serial constraint)
        mock_db_session.commit.side_effect = IntegrityError("UNIQUE constraint failed: hologram_devices.serial_number", "", "")
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.register_device(
                user_id=user_id,
                serial=sample_device_data["serial"],
                name=sample_device_data["name"]
            )
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_device_empty_serial(self, device_service, mock_db_session):
        """Test device registration with empty serial number"""
        user_id = uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.register_device(
                user_id=user_id,
                serial="",
                name="Test Device"
            )
        
        assert exc_info.value.status_code == 422
        assert "Serial number is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_device_integrity_error(self, device_service, mock_db_session, sample_device_data):
        """Test device registration with database integrity error"""
        user_id = uuid4()
        
        # Mock no existing device
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Mock integrity error on commit
        mock_db_session.commit.side_effect = IntegrityError("", "", "")
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.register_device(
                user_id=user_id,
                serial=sample_device_data["serial"],
                name=sample_device_data["name"]
            )
        
        assert exc_info.value.status_code == 500
        mock_db_session.rollback.assert_called_once()


class TestDeviceServiceGet:
    """Test cases for getting devices"""

    @pytest.mark.asyncio
    async def test_get_device_by_id_success(self, device_service, mock_db_session):
        """Test successful device retrieval by ID"""
        user_id = uuid4()
        device_id = uuid4()
        
        mock_device = HologramDevice(
            id=device_id,
            user_id=user_id,
            serial_number="TEST123",
            name="Test Device",
            device_type=DeviceType.hologram_fan,
            status=DeviceStatus.online
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_device
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.get_device_by_id(user_id, device_id)
        
        assert result == mock_device

    @pytest.mark.asyncio
    async def test_get_device_by_id_not_found(self, device_service, mock_db_session):
        """Test device retrieval when device not found"""
        user_id = uuid4()
        device_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.get_device_by_id(user_id, device_id)
        
        assert exc_info.value.status_code == 404
        assert "Device not found" in exc_info.value.detail


class TestDeviceServiceList:
    """Test cases for listing devices"""

    @pytest.mark.asyncio
    async def test_list_devices_success(self, device_service, mock_db_session):
        """Test successful device listing"""
        user_id = uuid4()
        
        mock_devices = [
            HologramDevice(id=uuid4(), user_id=user_id, serial_number="TEST1", name="Device 1"),
            HologramDevice(id=uuid4(), user_id=user_id, serial_number="TEST2", name="Device 2")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_devices
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.list_devices(user_id)
        
        assert len(result) == 2
        assert result == mock_devices

    @pytest.mark.asyncio
    async def test_list_devices_with_status_filter(self, device_service, mock_db_session):
        """Test device listing with status filter"""
        user_id = uuid4()
        
        mock_devices = [
            HologramDevice(id=uuid4(), user_id=user_id, serial_number="TEST1", name="Device 1", status=DeviceStatus.online)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_devices
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.list_devices(user_id, status=DeviceStatus.online)
        
        assert len(result) == 1
        assert result == mock_devices

    @pytest.mark.asyncio
    async def test_list_devices_with_pagination(self, device_service, mock_db_session):
        """Test device listing with pagination"""
        user_id = uuid4()
        
        mock_devices = [HologramDevice(id=uuid4(), user_id=user_id, serial_number="TEST1", name="Device 1")]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_devices
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.list_devices(user_id, page=1, per_page=1)
        
        assert len(result) == 1
        assert result == mock_devices


class TestDeviceServiceUpdate:
    """Test cases for updating devices"""

    @pytest.mark.asyncio
    async def test_update_device_success(self, device_service, mock_db_session):
        """Test successful device update"""
        user_id = uuid4()
        device_id = uuid4()
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.rowcount = 1
        mock_db_session.execute.return_value = mock_update_result
        
        # Mock get_device_by_id call
        mock_device = HologramDevice(
            id=device_id,
            user_id=user_id,
            serial_number="TEST123",
            name="Updated Device",
            device_type=DeviceType.hologram_fan,
            status=DeviceStatus.online
        )
        
        # Mock the get_device_by_id call
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_device
        mock_db_session.execute.side_effect = [mock_update_result, mock_get_result]
        
        update_data = {"name": "Updated Device", "status": DeviceStatus.online}
        result = await device_service.update_device(user_id, device_id, update_data)
        
        assert result == mock_device
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_device_not_found(self, device_service, mock_db_session):
        """Test device update when device not found"""
        user_id = uuid4()
        device_id = uuid4()
        
        # Mock update result with no rows affected
        mock_update_result = Mock()
        mock_update_result.rowcount = 0
        mock_db_session.execute.return_value = mock_update_result
        
        update_data = {"name": "Updated Device"}
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.update_device(user_id, device_id, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Device not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_device_empty_payload(self, device_service, mock_db_session):
        """Test device update with empty payload"""
        user_id = uuid4()
        device_id = uuid4()
        
        update_data = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.update_device(user_id, device_id, update_data)
        
        assert exc_info.value.status_code == 422
        assert "No valid fields to update" in exc_info.value.detail


class TestDeviceServiceDelete:
    """Test cases for deleting devices"""

    @pytest.mark.asyncio
    async def test_delete_device_success(self, device_service, mock_db_session):
        """Test successful device deletion"""
        user_id = uuid4()
        device_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.delete_device(user_id, device_id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_device_not_found(self, device_service, mock_db_session):
        """Test device deletion when device not found"""
        user_id = uuid4()
        device_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.delete_device(user_id, device_id)
        
        assert exc_info.value.status_code == 404
        assert "Device not found" in exc_info.value.detail


class TestDeviceServiceCount:
    """Test cases for counting devices"""

    @pytest.mark.asyncio
    async def test_count_devices_success(self, device_service, mock_db_session):
        """Test successful device counting"""
        user_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalar.return_value = 5
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.count_devices(user_id)
        
        assert result == 5

    @pytest.mark.asyncio
    async def test_count_devices_with_status(self, device_service, mock_db_session):
        """Test device counting with status filter"""
        user_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalar.return_value = 2
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.count_devices(user_id, status=DeviceStatus.online)
        
        assert result == 2


class TestDeviceServiceUtility:
    """Test cases for utility methods"""

    @pytest.mark.asyncio
    async def test_update_device_status_success(self, device_service, mock_db_session):
        """Test successful device status update"""
        device_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.update_device_status(device_id, DeviceStatus.online)
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_device_status_not_found(self, device_service, mock_db_session):
        """Test device status update when device not found"""
        device_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await device_service.update_device_status(device_id, DeviceStatus.online)
        
        assert exc_info.value.status_code == 404
        assert "Device not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_device_by_serial_success(self, device_service, mock_db_session):
        """Test successful device retrieval by serial"""
        serial = "TEST123"
        
        mock_device = HologramDevice(
            id=uuid4(),
            serial_number=serial,
            name="Test Device",
            device_type=DeviceType.hologram_fan,
            status=DeviceStatus.online
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_device
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.get_device_by_serial(serial)
        
        assert result == mock_device

    @pytest.mark.asyncio
    async def test_cleanup_offline_devices_success(self, device_service, mock_db_session):
        """Test successful cleanup of offline devices"""
        mock_result = Mock()
        mock_result.rowcount = 3
        mock_db_session.execute.return_value = mock_result
        
        result = await device_service.cleanup_offline_devices(hours_threshold=24)
        
        assert result == 3
        mock_db_session.commit.assert_called_once()
