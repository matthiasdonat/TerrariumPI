import os
import sys
import subprocess
import time
import terrariumLogging
from terrariumUtils import terrariumUtils

from . import terrariumRelayDimmer
logger = terrariumLogging.logging.getLogger(__name__)

class terrariumRelayDimmerLeddyTube(terrariumRelayDimmer):
    HARDWARE = "leddy-tube-dimmer"
    NAME = "LeddyTube"

    def _lade_zustand(self) -> int:
        """Lädt den Zustand. Bei Systemneustart (/tmp gelöscht) automatisch 0."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return int(f.read().strip())
            except (ValueError, OSError):
                return 0
        return 0

    def _speichere_zustand(self, wert: int):
        try:
            with open(self.state_file, "w") as f:
                f.write(str(int(wert)))
        except OSError as e:
            logger.error("Konnte Zustand nicht speichern: %s", e)

    def _load_hardware(self):
        logger.info(f"Loaded leddy-tube-dimmer.")

        self.gpio_pin = terrariumUtils.to_BCM_port_number(self._address[0])
        self.state_file = f"/tmp/aquael_state_gpio{self.gpio_pin}.txt"
        return "leddy" + self._address[0]

    def _schalte_steckdose(self, einschalten: bool) -> bool:
        """Führt den gpioset-Befehl aus."""
        wert = "0" if einschalten else "1"
        try:
            subprocess.run(["gpioset", "0", f"{self.gpio_pin}={wert}"], check=True)
            return True
        except subprocess.SubprocessError as e:
            logger.error("LeddyTubeDimmerRelais gpioset Fehler: %s", str(e))
            return False

    def _ermittle_modus(self, wert: int) -> int:
        """0=AUS, 1=DAY, 2=DAYBREAK, 3=NIGHT"""
        if wert == 0:
            return 0
        if 1 <= wert <= 35:
            return 3
        if 36 <= wert <= 70:
            return 2
        return 1

    def _klick(self) -> bool:
        """Erzeugt einen Schaltimpuls."""
        if not self._schalte_steckdose(False):
            return False
        time.sleep(1.0)
        return self._schalte_steckdose(True)

    def _set_hardware_value(self, value):
        try:
            ziel_wert = int(float(value))
        except (ValueError, TypeError):
            logger.error("Ungültiger Dimmer-Wert: %s", value)
            return False

        if not (0 <= ziel_wert <= 100):
            logger.error("Wert außerhalb des Bereichs (0-100): %d", ziel_wert)
            return False

        aktueller_wert = self._lade_zustand()
        akt_mod = self._ermittle_modus(aktueller_wert)
        ziel_mod = self._ermittle_modus(ziel_wert)

        if akt_mod == ziel_mod:
            self._speichere_zustand(ziel_wert)
            return True

        if ziel_mod == 0:
            if not self._schalte_steckdose(False):
                return False

        elif akt_mod == 0:
            if not self._schalte_steckdose(True):
                return False
            if ziel_mod == 2:
                time.sleep(1.5)
                if not self._klick():
                    return False
            elif ziel_mod == 3:
                time.sleep(1.5)
                if not self._klick():
                    return False
                time.sleep(1.5)
                if not self._klick():
                    return False

        elif akt_mod == 1:
            if ziel_mod == 2:
                if not self._klick():
                    return False
            elif ziel_mod == 3:
                if not self._klick():
                    return False
                time.sleep(1.5)
                if not self._klick():
                    return False

        elif akt_mod == 2:
            if ziel_mod == 3:
                if not self._klick():
                    return False
            elif ziel_mod == 1:
                if not self._schalte_steckdose(False):
                    return False
                time.sleep(5.5)
                if not self._schalte_steckdose(True):
                    return False

        elif akt_mod == 3:
            if not self._schalte_steckdose(False):
                return False
            time.sleep(5.5)
            if not self._schalte_steckdose(True):
                return False
            if ziel_mod == 2:
                time.sleep(1.5)
                if not self._klick():
                    return False

        self._speichere_zustand(ziel_wert)
        return True

    def _get_hardware_value(self):
        return float(self._lade_zustand())
