"""
PTech Wind Turbine Manufacturing - Company Profile
Specializing in high-precision Wind Turbine manufacturing and assembly
"""

COMPANY_PROFILE = {
    "name": "PTech",
    "facility": "PTech Wind Turbine Manufacturing Plant",
    "location": "Austin, TX",
    "specialization": "Wind Turbine Component Manufacturing",
    "production_lines": {
        "turbine_line_1": {
            "name": "Blade Production Line",
            "components": ["Blade", "Resin Infusion", "Curing Oven"],
            "sensor_config": {
                "temperature": {
                    "normal_range": (15.0, 30.0),
                    "warning_range": (30.0, 35.0),
                    "critical_range": (35.0, float('inf')),
                    "sensor_location": "Blade Section"
                },
                "humidity": {
                    "normal_range": (30.0, 60.0),
                    "warning_range": (60.0, 75.0),
                    "critical_range": (75.0, float('inf')),
                    "sensor_location": "Blade Section"
                },
                "sound": {
                    "normal_range": (45.0, 70.0),
                    "warning_range": (70.0, 80.0),
                    "critical_range": (80.0, float('inf')),
                    "sensor_location": "Blade Section"
                }
            }
        },
        "turbine_line_2": {
            "name": "Nacelle Assembly Line",
            "components": ["Nacelle", "Gearbox", "Generator"],
            "sensor_config": {
                "temperature": {
                    "normal_range": (15.0, 30.0),
                    "warning_range": (30.0, 35.0),
                    "critical_range": (35.0, float('inf')),
                    "sensor_location": "Nacelle Section"
                },
                "humidity": {
                    "normal_range": (30.0, 60.0),
                    "warning_range": (60.0, 75.0),
                    "critical_range": (75.0, float('inf')),
                    "sensor_location": "Nacelle Section"
                },
                "sound": {
                    "normal_range": (45.0, 70.0),
                    "warning_range": (70.0, 80.0),
                    "critical_range": (80.0, float('inf')),
                    "sensor_location": "Nacelle Section"
                }
            }
        }
    },
    "production_metrics": {
        "daily_blades": 20,
        "quality_target": 99.95,
        "cycle_time": 180,
        "operational_hours": 24
    },
    "anomaly_thresholds": {
        "temperature": {
            "warning": 0.6,
            "critical": 0.8
        },
        "humidity": {
            "warning": 0.6,
            "critical": 0.8
        },
        "sound": {
            "warning": 0.6,
            "critical": 0.8
        }
    }
} 