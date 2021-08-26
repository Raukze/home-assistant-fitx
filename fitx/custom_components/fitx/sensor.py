"""GitHub sensor platform."""
import logging
import re
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

import requests
from bs4 import BeautifulSoup
import voluptuous as vol
from aiohttp import ClientError

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import (
    ATTR_ADRESS,
    ATTR_STUDIO_NAME,
    ICON,
    CONF_LOCATIONS,
    CONF_STUDIO,
    SENSOR_PREFIX,
    BASE_API_URL,
)


_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
    vol.Required(CONF_LOCATIONS): vol.All(cv.ensure_list, [cv.string]),
    vol.Required(CONF_STUDIO): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    sensors = [FitxSensor(location) for location in config[CONF_LOCATIONS]]
    async_add_entities(sensors, update_before_add=True)


class FitxSensor(Entity):

    def __init__(self, config):
        self._state = None
        self._id = config['id'].lower().replace(" ", "-")
        self._name = config['id']

        if 'name' in config:
            self._name = config['name']

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return SENSOR_PREFIX + self._id

    @property
    def state(self) -> Optional[str]:
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return ICON

    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self.attrs

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            # get state
            url = f"{BASE_API_URL}{self._id}"
            website = requests.get(url)
            soup = BeautifulSoup(website.content, 'html.parser')

            self.attrs[ATTR_STUDIO_NAME] = str(soup.find("h1", class_="studio_hero__headline")).split("</span>")[1].split("</h1>")[0]
            self.attrs[ATTR_ADRESS] = str(soup.find("p", class_="studio_hero__address")).split(">\n          ")[1].split("        </p>")[0].replace(" · ", ", ")
            studioGraph = soup.find("section", class_="studio_graph")
            self._state = int(studioGraph["data-current-day-data"][1:-1].split(",")[-1])
            if self._state is None:
                raise Exception
            self._available = True
        except (ClientError):
            self._available = False
            _LOGGER.exception("Error retrieving data from FitX website.")
