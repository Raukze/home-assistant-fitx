"""FitX sensor platform."""
import logging

import json
import voluptuous as vol
from datetime import timedelta

from homeassistant.components.rest.data import RestData
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    PERCENTAGE,
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

from .const import (
    ATTR_ADDRESS,
    ATTR_ID,
    ATTR_STUDIO_NAME,
    ATTR_URL,
    CONF_ID,
    DEFAULT_ENDPOINT,
    ICON,
    CONF_LOCATIONS,
    REQUEST_AUTH,
    REQUEST_HEADERS,
    REQUEST_METHOD,
    REQUEST_PAYLOAD,
    REQUEST_VERIFY_SSL,
)

SCAN_INTERVAL = timedelta(minutes=10)

STUDIO_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LOCATIONS): vol.All(cv.ensure_list, [STUDIO_SCHEMA]),
    }
)

class FitxRequestError(Exception):
    """Error to indicate a FitX website request has failed."""
    pass

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # sensors = [FitxSensor(hass, location) for location in config[CONF_LOCATIONS]]
    sensors = []
    for location in config[CONF_LOCATIONS]:
        id = location[CONF_ID]
        url = DEFAULT_ENDPOINT.format(id=id)
        name = location[CONF_ID]
        if CONF_NAME in location:
            name = location[CONF_NAME]

        rest = RestData(hass, REQUEST_METHOD, url, REQUEST_AUTH, REQUEST_HEADERS, None, REQUEST_PAYLOAD, REQUEST_VERIFY_SSL)
        await rest.async_update()

        if rest.data is None:
            raise PlatformNotReady
        
        sensors.append(FitxSensor(rest, id, name))

    async_add_entities(sensors, update_before_add=True)


class FitxSensor(SensorEntity):
    """Representation of a FitX sensor."""

    def __init__(self, rest, id, name):
        """Initialize a FitX sensor."""
        self.rest = rest
        self._id = id
        # TODO: Get attributes from https://mein.fitx.de/nox/public/v1/studios
        self._attrs = {
                        ATTR_ID: self._id
                      }
        self._name = self._id
        self._state = None
        self._available = True

        if name is not None:
            self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._id

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return PERCENTAGE

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attrs

    def _get_raw_data(self):
        """Parse the html extraction in the executor."""
        raw_data = json.loads(self.rest.data)
        _LOGGER.debug(raw_data)
        return raw_data

    async def async_update(self):
        """Get the latest data from the source and updates the state."""
        await self.rest.async_update()
        await self._async_update_from_rest_data()

    async def async_added_to_hass(self):
        """Ensure the data from the initial update is reflected in the state."""
        await self._async_update_from_rest_data()

    async def _async_update_from_rest_data(self):
        """Update state from the rest data."""
        if self.rest.data is None:
            _LOGGER.error("Unable to retrieve data for %s", self.name)
            return

        try:
            raw_data = await self.hass.async_add_executor_job(self._get_raw_data)
            
            items = raw_data["items"]
            current = None

            for item in items:
                if item["isCurrent"]:
                    current = item
                    break
            
            if current is None:
                raise FitxRequestError
            
            self._state = current["percentage"]

            if self._state is None:
                raise FitxRequestError
            self._available = True
        except FitxRequestError:
            self._available = False
            _LOGGER.exception("Error retrieving data from FitX website.")
            return