# -*- coding: utf-8 -*-
from . import terrariumAnalogSensor


class terrariumMCP3008Sensor(terrariumAnalogSensor):
    HARDWARE = "mcp3008"
    TYPES = ["ph","temperature","water_flow"]
    NAME = "MCP3008 analog sensor"

    def _get_data(self):
        data = {}
        voltage = super()._get_data()
        data["ph"] = voltage
        data["temperature"] = voltage
        data["water_flow"] = voltage
        return data
