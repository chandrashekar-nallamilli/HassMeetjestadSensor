"""
Sensor support for meetjestad data service.
"""

from datetime import timedelta
from logging import getLogger

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY, ATTR_WEATHER_TEMPERATURE)
from homeassistant.const import (
     CONF_NAME, HTTP_OK, TEMP_CELSIUS, CONF_MONITORED_CONDITIONS)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = getLogger(__name__)

CONF_STATION_ID = 'station_id'

DEFAULT_NAME = 'meetjestad'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

SENSOR_TYPES = {
    ATTR_WEATHER_TEMPERATURE: ['Temperature', TEMP_CELSIUS, 'mdi:thermometer'],
    ATTR_WEATHER_HUMIDITY: ['Humidity', '%', 'mdi:water-percent'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, vol.Length(min=1), [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    name = config.get(CONF_NAME)
    station_id = config.get(CONF_STATION_ID)

    meetjestad_data = MeetjestadData(station_id=station_id)
    try:
        meetjestad_data.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Received error from AEMET: %s", err)
        return False

    add_entities([MeetjestadSensor(meetjestad_data, variable, name)
                  for variable in config[CONF_MONITORED_CONDITIONS]], True)


class MeetjestadSensor(Entity):
    """Representation of a sensor in the AEMET service."""

    def __init__(self, meetjestadData, variable, name):
        """Initialize the sensor."""
        self.meetjestadData = meetjestadData
        self.client_name = name
        self.variable = variable

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self.variable)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.meetjestadData.get_data(self.variable)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return SENSOR_TYPES[self.variable][1]

    @property
    def icon(self):
        """Return sensor specific icon."""
        return SENSOR_TYPES[self.variable][2]

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
        }

    def update(self):
        """Delegate update to data class."""
        self.meetjestadData.update()


class MeetjestadData:
    """Get the latest data and updates the states."""

    API_URL_BASE = 'https://meetjescraper.online'

    def __init__(self, station_id):
        """Initialize the data object."""
        self._station_id = station_id
        self.data = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.debug("------- Updating AEMET sensor")
        params = {'sensor': self._station_id, 'limit': 2}
        main_rsp = requests.get(self.API_URL_BASE, params=params)
        if main_rsp.status_code != HTTP_OK:
            _LOGGER.error("Invalid response: %s", main_rsp.status_code)
            return

        main_result = main_rsp.json()
        self.set_data(main_result)
        _LOGGER.debug(main_result)

    def set_data(self, record):
        """Set data using the last record from API."""
        state = {ATTR_WEATHER_TEMPERATURE: record[0]['temperature'], ATTR_WEATHER_HUMIDITY: record[0]['humidity']}

        self.data = state

    def get_data(self, variable):
        """Get the data."""
        return self.data.get(variable)
