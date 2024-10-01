import voluptuous as vol
import logging
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA
)
from homeassistant.const import UnitOfInformation, CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from client import TendaClient


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})


_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    host = config[CONF_HOST]
    password = config.get(CONF_PASSWORD)
    client = TendaClient(host, password)
    add_entities([TendaUploadSensor(client), TendaDownloadSensor(client)])


class TendaUploadSensor(SensorEntity):

    _attr_name = "Tenda Router Upload Speed"
    _attr_native_unit_of_measurement = UnitOfInformation.KILOBYTES
    _attr_device_class = SensorDeviceClass.DATA_RATE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _client: TendaClient = None

    def __init__(self, client, *args, **kwargs):
        self._client = client
        super(TendaUploadSensor, self).__init__(*args, **kwargs)

    def update(self) -> None:
        self._attr_native_value = 0
        network = self._client.get_network_status()['getNetwork']
        if not network:
            return

        # only get one wan status now
        network = network[0]
        speed = network['wanUpFlux']

        rate = float(speed[-4:])
        measurement = speed[:-4]
        if measurement == 'MB/s':
            rate = rate * 1024.0

        self._attr_native_value = rate


class TendaDownloadSensor(SensorEntity):

    _attr_name = "Tenda Router Download Speed"
    _attr_native_unit_of_measurement = UnitOfInformation.KILOBYTES
    _attr_device_class = SensorDeviceClass.DATA_RATE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _client = None

    def __init__(self, client, *args, **kwargs):
        self._client = client
        super(TendaDownloadSensor, self).__init__(*args, **kwargs)

    def update(self) -> None:
        self._attr_native_value = 0
        network = self._client.get_network_status()['getNetwork']
        if not network:
            return

        # only get one wan status now
        network = network[0]
        speed = network['wanDownFlux']

        rate = float(speed[-4:])
        measurement = speed[:-4]
        if measurement == 'MB/s':
            rate = rate * 1024.0

        self._attr_native_value = rate
