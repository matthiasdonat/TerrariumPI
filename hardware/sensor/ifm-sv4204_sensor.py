# -*- coding: utf-8 -*-
from . import terrariumAnalogSensor


class terrariumIfmSv4204Sensor(terrariumAnalogSensor):
    HARDWARE = "ifmsv4204"
    TYPES = ["temperature","water_flow"]
    NAME = "ifm sv4204 analog sensor"

    def _get_data(self):
        data = {}
        voltage = super()._get_data() * 3.3

	# ==========================================
	# KONFIGURATION & GRENZWERTE (ifm SV4202)
	# ==========================================

	# Gemeinsame Spannungswerte für 4-20 mA an 150 Ohm
        V_MIN = 0.60  # Spannung bei 4 mA
        V_MAX = 3.00  # Spannung bei 20 mA

        # Durchfluss-Parameter (Kanal CH0)
        MIN_FLOW = 1.0   # l/min bei 4 mA
        MAX_FLOW = 20.0  # l/min bei 20 mA

	# Temperatur-Parameter (Kanal CH1)
        MIN_TEMP = -10.0 # °C bei 4 mA
        MAX_TEMP = 90.0  # °C bei 20 mA

	# ==========================================

        if voltage < V_MIN:
            res = 0.0
        elif voltage > V_MAX:
            res = MAX_FLOW
        else:
            res = MIN_FLOW + ((voltage - V_MIN) / (V_MAX - V_MIN)) * (MAX_FLOW - MIN_FLOW)
        data["water_flow"] = res

        if voltage < V_MIN:
            res = MIN_TEMP
        elif voltage > V_MAX:
            res = MAX_TEMP
        else:
            res = MIN_TEMP + ((voltage - V_MIN) / (V_MAX - V_MIN)) * (MAX_TEMP - MIN_TEMP)

        data["temperature"] = res

        return data

