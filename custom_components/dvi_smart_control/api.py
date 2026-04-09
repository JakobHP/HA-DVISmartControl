"""API client for DVI Smart Control portal."""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from .const import (
    COMMAND_TIMEOUT,
    DATA_TIMEOUT,
    INFO_ENERGY,
    INFO_ERRORS,
    INFO_STATUS,
    KEY_COMPRESSOR_HOURS,
    KEY_COMPRESSOR_RUNNING,
    KEY_CURRENT_ERRORS,
    KEY_ENERGY_CONSUMED_KW,
    KEY_ENERGY_CONSUMED_KWH,
    KEY_ENERGY_DELIVERED_KW,
    KEY_ENERGY_DELIVERED_KWH,
    KEY_FAN_RUNNING,
    KEY_FLOW_RATE,
    KEY_HEATING_FLOW_TEMP,
    KEY_HEATING_RETURN_TEMP,
    KEY_HEATING_SYSTEM_STATE,
    KEY_HEATING_TEMP_OFFSET_VALUE,
    KEY_HOT_WATER_CLOCK_STATE,
    KEY_HOT_WATER_HOURS,
    KEY_HOT_WATER_STATE,
    KEY_HOT_WATER_TEMP,
    KEY_HOT_WATER_TEMP_SETPOINT,
    KEY_INSTALLATION_DATE,
    KEY_LAST_UPDATE,
    KEY_MANUFACTURING_NUMBER,
    KEY_OUTDOOR_TEMP,
    KEY_ROOM_TEMP,
    KEY_SOFTWARE_VERSION,
    KEY_SUPPLEMENTARY_HEAT_HOURS,
    KEY_SUPPLEMENTARY_HEATING_STATE,
    KEY_TANK_TEMP,
    PARAM_UPDATE_BUTTONS,
    PARAM_UPDATE_GRAPHICS,
    PARAM_USER_SETTING,
    URL_MAIN,
    URL_PROCESS,
    URL_PUMP_INFO,
)

_LOGGER = logging.getLogger(__name__)

# Map CSS class -> data key for temperature extraction
_TEMP_CLASS_MAP = {
    "value7": KEY_OUTDOOR_TEMP,
    "value5": KEY_TANK_TEMP,
    "value3": KEY_HOT_WATER_TEMP,
    "value1": KEY_HEATING_FLOW_TEMP,
    "value2": KEY_HEATING_RETURN_TEMP,
    "value8": KEY_ROOM_TEMP,
}

# GIF image patterns for component state detection
# A1 = outdoor unit/fan, A4 = compressor area, A5 = expansion valve area
# The number after the dash indicates state (0 = off typically)
_RE_FAN_GIF = re.compile(r"A1-(\d+)\.gif")
_RE_COMPRESSOR_GIF = re.compile(r"A4-(\d+)\.gif")


class DviSmartControlAuthError(Exception):
    """Authentication failed."""


class DviSmartControlConnectionError(Exception):
    """Connection to portal failed."""


class DviSmartControlApiClient:
    """Client for the DVI Smart Control web portal."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._lock = asyncio.Lock()
        self._authenticated = False
        # We manage our own cookie jar via the session
        # PHP session cookie is handled automatically by aiohttp

    async def authenticate(self) -> bool:
        """Log in to the portal. Returns True on success."""
        try:
            # POST login form to process.php (matching the portal's form action)
            resp = await self._session.post(
                f"{self._base_url}{URL_PROCESS}",
                data={
                    "user": self._username,
                    "pass": self._password,
                    "sublogin": "1",
                    "Remember": "on",
                },
                timeout=aiohttp.ClientTimeout(total=DATA_TIMEOUT),
                allow_redirects=True,
            )

            # Successful login redirects to main.php
            if URL_MAIN in str(resp.url):
                self._authenticated = True
                _LOGGER.debug("Successfully authenticated with DVI portal")
                return True

            # Check if we landed back on the login page (failed auth)
            text = await resp.text()
            if self._is_login_page(text):
                self._authenticated = False
                raise DviSmartControlAuthError("Invalid credentials")

            # Unexpected response
            self._authenticated = False
            raise DviSmartControlAuthError(
                f"Unexpected response during login: {resp.status}"
            )

        except aiohttp.ClientError as err:
            self._authenticated = False
            raise DviSmartControlConnectionError(
                f"Connection failed: {err}"
            ) from err

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid session, re-authenticating if needed."""
        if not self._authenticated:
            await self.authenticate()

    def _is_login_page(self, text: str) -> bool:
        """Check if the response is a login page (session expired)."""
        return "Log ind!" in text and 'name="user"' in text

    async def _post_process(
        self, data: dict[str, Any], timeout: float = DATA_TIMEOUT
    ) -> str:
        """POST to process.php with auto re-auth."""
        await self._ensure_authenticated()

        resp = await self._session.post(
            f"{self._base_url}{URL_PROCESS}",
            data=data,
            timeout=aiohttp.ClientTimeout(total=timeout),
        )
        text = await resp.text()

        # Session expired — re-authenticate and retry once
        if self._is_login_page(text):
            _LOGGER.debug("Session expired, re-authenticating")
            self._authenticated = False
            await self.authenticate()
            resp = await self._session.post(
                f"{self._base_url}{URL_PROCESS}",
                data=data,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            text = await resp.text()
            if self._is_login_page(text):
                raise DviSmartControlAuthError("Re-authentication failed")

        return text

    async def _get_pump_info(self, info_id: str) -> str:
        """GET pumpinfo.php with auto re-auth."""
        await self._ensure_authenticated()

        resp = await self._session.get(
            f"{self._base_url}{URL_PUMP_INFO}",
            params={"id": info_id},
            timeout=aiohttp.ClientTimeout(total=DATA_TIMEOUT),
        )
        text = await resp.text()

        if self._is_login_page(text):
            _LOGGER.debug("Session expired, re-authenticating")
            self._authenticated = False
            await self.authenticate()
            resp = await self._session.get(
                f"{self._base_url}{URL_PUMP_INFO}",
                params={"id": info_id},
                timeout=aiohttp.ClientTimeout(total=DATA_TIMEOUT),
            )
            text = await resp.text()
            if self._is_login_page(text):
                raise DviSmartControlAuthError("Re-authentication failed")

        return text

    async def _get_pumpchoice(self, choice_id: str) -> str:
        """GET pumpchoice.php with auto re-auth."""
        await self._ensure_authenticated()

        resp = await self._session.get(
            f"{self._base_url}/includes/pumpchoice.php",
            params={"id": choice_id},
            timeout=aiohttp.ClientTimeout(total=DATA_TIMEOUT),
        )
        text = await resp.text()

        if self._is_login_page(text):
            self._authenticated = False
            await self.authenticate()
            resp = await self._session.get(
                f"{self._base_url}/includes/pumpchoice.php",
                params={"id": choice_id},
                timeout=aiohttp.ClientTimeout(total=DATA_TIMEOUT),
            )
            text = await resp.text()
            if self._is_login_page(text):
                raise DviSmartControlAuthError("Re-authentication failed")

        return text

    # ── Data fetching ──────────────────────────────────────────────

    async def async_get_all_data(self) -> dict[str, Any]:
        """Fetch all sensor data. Must be called from executor for BS4."""
        async with self._lock:
            data: dict[str, Any] = {}

            # Fetch graphics (temperatures + component states)
            graphics_html = await self._post_process(
                {PARAM_UPDATE_GRAPHICS: "1"}
            )
            data.update(self._parse_graphics(graphics_html))

            # Fetch status info (hour counters, install date, etc.)
            status_html = await self._get_pump_info(INFO_STATUS)
            data.update(self._parse_status(status_html))

            # Fetch energy meters
            energy_html = await self._get_pump_info(INFO_ENERGY)
            data.update(self._parse_energy(energy_html))

            # Fetch error list
            errors_html = await self._get_pump_info(INFO_ERRORS)
            data.update(self._parse_errors(errors_html))

            # Fetch current control states
            data.update(await self._fetch_control_states())

            return data

    async def _fetch_control_states(self) -> dict[str, Any]:
        """Fetch current values of all user-controllable settings."""
        data: dict[str, Any] = {}

        # Heating system (pumpchoice 11, setting 1)
        html = await self._get_pumpchoice("11")
        data[KEY_HEATING_SYSTEM_STATE] = self._parse_toggle_state(html)

        # Heating temp offset (pumpchoice 12, setting 2)
        html = await self._get_pumpchoice("12")
        data[KEY_HEATING_TEMP_OFFSET_VALUE] = self._parse_numeric_value(html, "user2")

        # Hot water (pumpchoice 21, setting 10)
        html = await self._get_pumpchoice("21")
        data[KEY_HOT_WATER_STATE] = self._parse_toggle_state(html)

        # Hot water temp (pumpchoice 22, setting 11)
        html = await self._get_pumpchoice("22")
        data[KEY_HOT_WATER_TEMP_SETPOINT] = self._parse_numeric_value(html, "user11")

        # Hot water clock (pumpchoice 23, setting 12)
        html = await self._get_pumpchoice("23")
        data[KEY_HOT_WATER_CLOCK_STATE] = self._parse_select_state(html)

        # Supplementary heating (pumpchoice 14, setting 15)
        html = await self._get_pumpchoice("14")
        data[KEY_SUPPLEMENTARY_HEATING_STATE] = self._parse_select_state(html)

        return data

    # ── Commands ───────────────────────────────────────────────────

    async def async_set_user_setting(
        self, setting: str, value: str | int
    ) -> bool:
        """Send a user setting change to the pump."""
        async with self._lock:
            result = await self._post_process(
                {
                    PARAM_USER_SETTING: "1",
                    "setting": setting,
                    "value": str(value),
                },
                timeout=COMMAND_TIMEOUT,
            )
            success = result.strip() == "1"
            if not success:
                _LOGGER.warning(
                    "Setting %s=%s failed, response: %s",
                    setting,
                    value,
                    result[:100],
                )
            return success

    async def async_turn_pump_on(self) -> bool:
        """Turn the pump on."""
        return await self.async_set_user_setting("onoff", "2")

    async def async_turn_pump_off(self) -> bool:
        """Turn the pump off. Value 4 is the toggle used by the portal."""
        # The portal uses turnPumpOnOff(4) which toggles.
        # But to be explicit, we use value-based approach.
        # From the JS: value 2 = on ("Tændt"), anything else = off ("Slukket")
        # So to turn off, we use a value that isn't 2 (the portal uses 4)
        return await self.async_set_user_setting("onoff", "4")

    # ── HTML Parsing ───────────────────────────────────────────────

    @staticmethod
    def _parse_graphics(html: str) -> dict[str, Any]:
        """Parse the pump graphics HTML for temperatures and states."""
        data: dict[str, Any] = {}
        soup = BeautifulSoup(html, "html.parser")

        # Extract temperatures from span.temp elements
        for css_class, key in _TEMP_CLASS_MAP.items():
            elem = soup.find("span", class_=css_class)
            if elem:
                temp_str = elem.get_text(strip=True).replace("°", "").replace("&deg;", "")
                try:
                    data[key] = float(temp_str)
                except ValueError:
                    data[key] = None
            else:
                data[key] = None

        # Extract timestamp
        date_elem = soup.find("div", class_="sensordate")
        if date_elem:
            data[KEY_LAST_UPDATE] = date_elem.get_text(strip=True)

        # Extract component states from GIF image names
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")

            fan_match = _RE_FAN_GIF.search(src)
            if fan_match:
                # A1-0 = fan off, A1-1+ = fan running
                data[KEY_FAN_RUNNING] = fan_match.group(1) != "0"

            comp_match = _RE_COMPRESSOR_GIF.search(src)
            if comp_match:
                # A4-0 = off, A4-1+ = running (A4-5 means running at speed 5)
                data[KEY_COMPRESSOR_RUNNING] = comp_match.group(1) != "0"

        return data

    @staticmethod
    def _parse_status(html: str) -> dict[str, Any]:
        """Parse the status info page."""
        data: dict[str, Any] = {}
        soup = BeautifulSoup(html, "html.parser")

        # Installation date
        for td in soup.find_all("td"):
            p_elem = td.find("p")
            time_elem = td.find("time")
            if not p_elem or not time_elem:
                continue

            text = p_elem.get_text(strip=True).lower()
            value = time_elem.get_text(strip=True)

            if "installationsdato" in text or "installation" in text:
                data[KEY_INSTALLATION_DATE] = value
            elif "fabrikationsnummer" in text or "manufacturing" in text:
                data[KEY_MANUFACTURING_NUMBER] = value
            elif "software" in text:
                data[KEY_SOFTWARE_VERSION] = value

        # Hour counters from table-info2
        info_table = soup.find("table", class_="table-info2")
        if info_table:
            rows = info_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True).lower()
                    value_text = cells[1].get_text(strip=True)
                    try:
                        value = int(value_text)
                    except ValueError:
                        continue

                    if "kompressor" in label or "compressor" in label:
                        data[KEY_COMPRESSOR_HOURS] = value
                    elif "varmt vand" in label or "hot water" in label:
                        data[KEY_HOT_WATER_HOURS] = value
                    elif "tilskudsvarme" in label or "supplemental" in label:
                        data[KEY_SUPPLEMENTARY_HEAT_HOURS] = value

        return data

    @staticmethod
    def _parse_energy(html: str) -> dict[str, Any]:
        """Parse the energy meters info page."""
        data: dict[str, Any] = {}
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table", class_="table-info2")

        for table in tables:
            header_td = table.find("td", attrs={"colspan": "2"})
            if not header_td:
                continue
            header_text = header_td.get_text(strip=True).lower()

            is_consumed = "tilført" in header_text or "added" in header_text
            is_delivered = "afleveret" in header_text or "delivered" in header_text

            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) != 2:
                    continue
                label = cells[0].get_text(strip=True)
                value_text = cells[1].get_text(strip=True)

                try:
                    value = float(value_text)
                except ValueError:
                    continue

                if is_consumed:
                    if label == "kWh":
                        data[KEY_ENERGY_CONSUMED_KWH] = value
                    elif label == "kW":
                        data[KEY_ENERGY_CONSUMED_KW] = value
                elif is_delivered:
                    if label == "kWh":
                        data[KEY_ENERGY_DELIVERED_KWH] = value
                    elif label == "kW":
                        data[KEY_ENERGY_DELIVERED_KW] = value
                    elif "flow" in label.lower():
                        data[KEY_FLOW_RATE] = value

        return data

    @staticmethod
    def _parse_errors(html: str) -> dict[str, Any]:
        """Parse the error list info page."""
        data: dict[str, Any] = {}
        soup = BeautifulSoup(html, "html.parser")

        # Look for current errors
        current_errors: list[str] = []
        tables = soup.find_all("table", class_="table-info3")

        if tables:
            # First table is current errors
            first_table = tables[0]
            rows = first_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    error_p = cells[1].find("p")
                    if error_p:
                        error_text = error_p.get_text(strip=True)
                        # Skip "no errors" message
                        if "ingen fejl" not in error_text.lower() and "no_registered" not in error_text.lower():
                            current_errors.append(error_text)

        data[KEY_CURRENT_ERRORS] = current_errors

        return data

    @staticmethod
    def _parse_toggle_state(html: str) -> bool | None:
        """Parse a toggle dialog (on/off) and return current state."""
        soup = BeautifulSoup(html, "html.parser")
        # The active option has a fa-check icon
        active = soup.find("i", class_="fa-check")
        if not active:
            return None

        # Walk up to the parent div with onclick
        parent_div = active.find_parent("div", attrs={"onclick": True})
        if not parent_div:
            return None

        onclick = parent_div["onclick"]
        # e.g. changeUserSetting(1,1,11) -> value is second arg
        match = re.search(r"changeUserSetting\(\w+,(\d+)", onclick)
        if match:
            return match.group(1) == "1"
        return None

    @staticmethod
    def _parse_numeric_value(html: str, element_id: str) -> float | None:
        """Parse a numeric spinner dialog for current value."""
        soup = BeautifulSoup(html, "html.parser")
        label = soup.find("label", id=element_id)
        if label:
            try:
                return float(label.get_text(strip=True))
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_select_state(html: str) -> str | None:
        """Parse a multi-option dialog and return the value of the active option."""
        soup = BeautifulSoup(html, "html.parser")
        active = soup.find("i", class_="fa-check")
        if not active:
            return None

        parent_div = active.find_parent("div", attrs={"onclick": True})
        if not parent_div:
            return None

        onclick = parent_div["onclick"]
        # e.g. changeUserSetting(15,1,14) -> value is second arg
        match = re.search(r"changeUserSetting\(\w+,(\d+)", onclick)
        if match:
            return match.group(1)
        return None
