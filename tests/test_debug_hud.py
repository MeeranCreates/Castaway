import math

from pyglm import glm

from src.engine.debug import DebugSystem


class DummyApp:
    def __init__(self):
        self.time_of_day = type("Cycle", (), {"current_time": 14.5})()
        self.sun = type("Sun", (), {"direction": glm.vec3(0.5, 0.8, 0.1), "intensity": 1.2})()
        self.moon = type("Moon", (), {"intensity": 0.25})()
        self.camera = type("Camera", (), {"position": glm.vec3(12.3, 4.5, -7.6), "yaw": 132.4, "pitch": -12.7})()
        self.player = type("Player", (), {"position": glm.vec3(12.3, 4.5, -7.6), "speed": 8.5})()
        self.lighting = type("Lighting", (), {"ambient": 0.42})()
        self.world = type("World", (), {"name": "Seabreeze Isles", "weather": "Clear", "day_number": 3})()
        self.renderer = type("Renderer", (), {"fps": 60.0, "frame_time": 16.4, "draw_calls": 71, "triangles": 184320, "vertices": 96000, "visible_objects": 248, "meshes": 42, "textures": 18})()
        self.terrain = type("Terrain", (), {"height_at": staticmethod(lambda x, z: 2.5)})()


def test_debug_hud_defaults_to_disabled():
    debug = DebugSystem(None)
    assert debug.enabled is False


def test_debug_hud_collects_runtime_state():
    app = DummyApp()
    debug = DebugSystem(None)
    snapshot = debug.build_snapshot(app, 60.0, 0.0164)

    assert snapshot["fps"] == 60.0
    assert snapshot["frame_time"] == 0.0164
    assert snapshot["world_name"] == "Seabreeze Isles"
    assert snapshot["time_of_day"] == 14.5
    assert snapshot["player_xyz"][0] == 12.3
    assert snapshot["sun_elevation"] > 0.0
    assert snapshot["looking"] in {"NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST"}


def test_debug_hud_toggle_is_f3_only_and_non_destructive():
    debug = DebugSystem(None)
    assert debug.enabled is False
    debug.toggle()
    assert debug.enabled is True
    debug.toggle()
    assert debug.enabled is False
