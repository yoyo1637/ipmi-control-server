from datetime import timedelta
import logging

from homeassistant.components.switch import SwitchEntity
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from pyghmi.ipmi import command

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ipmi_control"

SCAN_INTERVAL = timedelta(minutes=2)

SERVER_SCHEMA = vol.Schema({
    vol.Required("name"): cv.string,
    vol.Required("host"): cv.string,
    vol.Required("user"): cv.string,
    vol.Required("password"): cv.string,
})

PLATFORM_SCHEMA = vol.Schema({
    vol.Required("platform"): cv.string,
    vol.Required("servers"): vol.All(cv.ensure_list, [SERVER_SCHEMA]),
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    switches = []
    servers = config.get("servers", [])
    for server in servers:
        switch = IPMISwitch(server)
        switches.append(switch)
    async_add_entities(switches)

    async def handle_reset_service(call):
        entity_id = call.data.get('entity_id')
        for sw in switches:
            if sw.entity_id == entity_id:
                await sw.async_reset()
                return

    hass.services.async_register(
        DOMAIN, "reset_server", handle_reset_service,
        schema=vol.Schema({vol.Required("entity_id"): cv.entity_id})
    )

class IPMISwitch(SwitchEntity):
    def __init__(self, server):
        self._name = server["name"]
        self._host = server["host"]
        self._user = server["user"]
        self._password = server["password"]
        self._state = None
        self._conn = command.Command(bmc=self._host, userid=self._user, password=self._password)

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        _LOGGER.info(f"Powering ON server {self._name}")
        self._conn.set_power('on')
        await self.async_update()

    async def async_turn_off(self, **kwargs):
        _LOGGER.info(f"Powering OFF server {self._name}")
        self._conn.set_power('off')
        await self.async_update()

    async def async_reset(self):
        _LOGGER.info(f"Resetting (Reboot) server {self._name}")
        self._conn.set_power('reset')
        await self.async_update()

    async def async_update(self):
        try:
            power = self._conn.get_power()
            self._state = power.get('powerstate', '').lower() == 'on'
            _LOGGER.debug(f"{self._name} power state updated: {self._state}")
        except Exception as e:
            _LOGGER.error(f"Failed to update status of {self._name}: {e}")
