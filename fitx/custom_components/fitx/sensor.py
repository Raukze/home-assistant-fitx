"""FitX sensor platform."""
import logging

from bs4 import BeautifulSoup
import voluptuous as vol
from datetime import timedelta

from homeassistant.components.rest.data import RestData
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

from .const import (
    ATTR_ADDRESS,
    ATTR_STUDIO_NAME,
    CONF_ID,
    DEFAULT_ENDPOINT,
    DEFAULT_NAME,
    ICON,
    CONF_LOCATIONS,
    REQUEST_AUTH,
    REQUEST_HEADERS,
    REQUEST_METHOD,
    REQUEST_PAYLOAD,
    REQUEST_VERIFY_SSL,
    SENSOR_PREFIX,
    UNIT_OF_MEASUREMENT,
    SCAN_INTERVAL,
)

SCAN_INTERVAL = timedelta(minutes=SCAN_INTERVAL)

STUDIO_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
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
    sensors = [FitxSensor(hass, location) for location in config[CONF_LOCATIONS]]
    async_add_entities(sensors, update_before_add=True)


class FitxSensor(SensorEntity):
    """Representation of a FitX sensor."""

    def __init__(self, hass, location):
        """Initialize a FitX sensor."""
        self._state = None
        self._id = location[CONF_ID].lower().replace(" ", "-")
        self._url = DEFAULT_ENDPOINT.format(id=self._id)
        self._name = location[CONF_ID]

        if CONF_NAME in location:
            self._name = location[CONF_NAME]

        self.rest = RestData(hass, REQUEST_METHOD, self._url, REQUEST_AUTH, REQUEST_HEADERS, None, REQUEST_PAYLOAD, REQUEST_VERIFY_SSL)

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_PREFIX + self._id

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return UNIT_OF_MEASUREMENT

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    @property
    def native_value(self):
        """Return the state of the device."""
        return self._state

    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attrs

    def _get_raw_data(self):
        """Parse the html extraction in the executor."""
        raw_data = BeautifulSoup(self.rest.data, "html.parser")
        _LOGGER.debug(raw_data)
        return raw_data

    async def async_update(self):
        """Get the latest data from the source and updates the state."""
        await self.rest.async_update()
        await self._async_update_from_rest_data()

    async def async_added_to_hass(self):
        """Ensure the data from the initial update is reflected in the state."""
        await self.rest.async_update()

        if self.rest.data is None:
            raise PlatformNotReady
        
        await self._async_update_from_rest_data()

    async def _async_update_from_rest_data(self):
        """Update state from the rest data."""
        if self.rest.data is None:
            _LOGGER.error("Unable to retrieve data for %s", self.name)
            return

        try:
            raw_data = await self.hass.async_add_executor_job(self._get_raw_data)
            self.attrs[ATTR_STUDIO_NAME] = str(raw_data.find("h1", class_="studio_hero__headline")).split("</span>")[1].split("</h1>")[0]
            self.attrs[ATTR_ADDRESS] = str(raw_data.find("p", class_="studio_hero__address")).split(">\n          ")[1].split("        </p>")[0].replace(" · ", ", ")
            studioGraph = raw_data.find("section", class_="studio_graph")
            self._state = int(studioGraph["data-current-day-data"][1:-1].split(",")[-1])
            if self._state is None:
                raise FitxRequestError
            self._available = True
        except FitxRequestError:
            self._available = False
            _LOGGER.exception("Error retrieving data from FitX website.")