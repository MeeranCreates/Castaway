import math

from src.engine.time_of_day import TimeOfDay


def test_cycle_exposes_day_and_night_values():
    cycle = TimeOfDay()

    state = cycle.evaluate_at(0.0)
    assert state["sun_intensity"] <= 0.05
    assert state["moon_intensity"] > 0.2
    assert state["sky_bottom"][2] > 0.05

    noon = cycle.evaluate_at(12.0)
    assert noon["sun_intensity"] > 0.8
    assert noon["sun_direction"].y > 0.7
    assert noon["moon_intensity"] < 0.08

    sunrise = cycle.evaluate_at(6.0)
    assert sunrise["sun_intensity"] > 0.2
    assert sunrise["sun_color"][0] > 0.7


def test_cycle_is_continuous_between_states():
    cycle = TimeOfDay()
    a = cycle.evaluate_at(11.9)
    b = cycle.evaluate_at(12.1)

    assert abs(a["sun_intensity"] - b["sun_intensity"]) < 0.7
    assert abs(a["sky_horizon"][0] - b["sky_horizon"][0]) < 0.5
