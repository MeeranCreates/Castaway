import ctypes
import math
import os
import time

import glfw
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from .shader import Shader


FONT_5X7 = {
    " ": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    "0": [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    "1": [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "2": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
    "3": [0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110],
    "4": [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    "5": [0b11111, 0b10000, 0b10000, 0b11110, 0b00001, 0b00001, 0b11110],
    "6": [0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    "7": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    "8": [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    "9": [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b11100],
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "B": [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    "C": [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    "D": [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    "E": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    "F": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    "G": [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    "H": [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "I": [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "J": [0b00011, 0b00010, 0b00010, 0b00010, 0b10010, 0b10010, 0b01100],
    "K": [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    "L": [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    "M": [0b10001, 0b11011, 0b10101, 0b10001, 0b10001, 0b10001, 0b10001],
    "N": [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "P": [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    "Q": [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    "R": [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    "S": [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
    "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "U": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b01010, 0b00100],
    "W": [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b01010, 0b01010],
    "X": [0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b01010, 0b10001],
    "Y": [0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "Z": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    ":": [0b00000, 0b00110, 0b00110, 0b00000, 0b00110, 0b00110, 0b00000],
    ".": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00110, 0b00110],
    ",": [0b00000, 0b00000, 0b00000, 0b00000, 0b00110, 0b00110, 0b00100],
    "/": [0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000, 0b00000],
    "-": [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    "_": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
    "+": [0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
    "=": [0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000],
    "?": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100],
    "!": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    "\"": [0b01100, 0b01100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    "'": [0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    "(": [0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010],
    ")": [0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000],
    "[": [0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110],
    "]": [0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110],
    "%": [0b10000, 0b10001, 0b00010, 0b00100, 0b01000, 0b10001, 0b00000],
    "*": [0b00000, 0b01010, 0b00100, 0b11111, 0b00100, 0b01010, 0b00000],
    "#": [0b00100, 0b11111, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100],
    ";": [0b00000, 0b00110, 0b00110, 0b00000, 0b00110, 0b00110, 0b00100],
    "<": [0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
    ">": [0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
    "|": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "~": [0b00000, 0b00110, 0b11001, 0b00000, 0b00000, 0b00000, 0b00000],
}


class DebugSystem:
    """Lightweight developer HUD for player/world/render stats."""

    def __init__(self, window_handle):
        self.window_handle = window_handle
        self.enabled = False
        self.snapshot = {}
        self._f3_down = False
        self._last_refresh = 0.0
        self._hud_shader = None
        self._vao = None
        self._vbo = None

        if window_handle is not None:
            shader_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "shaders")
            self._hud_shader = Shader(
                os.path.join(shader_dir, "hud.vert"),
                os.path.join(shader_dir, "hud.frag"),
                {"aPosition": 0, "aColor": 1},
            )
            self._vao = glGenVertexArrays(1)
            self._vbo = glGenBuffers(1)
            glBindVertexArray(self._vao)
            glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 6 * ctypes.sizeof(ctypes.c_float), None)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 6 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))
            glBindVertexArray(0)

    def toggle(self):
        self.enabled = not self.enabled
        print(f"[DEBUG HUD] {'ON' if self.enabled else 'OFF'}")

    def update(self, dt, app):
        if self.window_handle is None:
            return

        f3 = glfw.get_key(self.window_handle, glfw.KEY_F3)
        if f3 == glfw.PRESS and not self._f3_down:
            self.toggle()
        self._f3_down = f3 == glfw.PRESS

        if self.enabled:
            now = time.perf_counter()
            if now - self._last_refresh >= 0.2:
                fps = 1.0 / max(dt, 1e-4)
                self.snapshot = self.build_snapshot(app, fps, dt)
                self._last_refresh = now

    def _format_time(self, hours):
        total_minutes = int((float(hours) % 24.0) * 60.0)
        hour = int(total_minutes // 60)
        minute = int(total_minutes % 60)
        return f"{hour:02d}:{minute:02d}"

    def _cardinal_direction(self, yaw_degrees):
        yaw = (yaw_degrees + 360.0) % 360.0
        if 315.0 <= yaw or yaw < 45.0:
            return "SOUTH"
        if 45.0 <= yaw < 135.0:
            return "WEST"
        if 135.0 <= yaw < 225.0:
            return "NORTH"
        return "EAST"

    def build_snapshot(self, app, fps, frame_time):
        camera = getattr(app, "camera", None)
        player = getattr(app, "player", None)
        sun = getattr(app, "sun", None)
        moon = getattr(app, "moon", None)
        terrain = getattr(app, "terrain", None)
        time_of_day = getattr(app, "time_of_day", None)
        world_name = getattr(app, "world_name", "Castaway")
        weather = getattr(app, "weather", "Clear")
        day_number = getattr(app, "day_number", 1)
        visible_objects = getattr(app, "visible_objects", len(getattr(getattr(app, "props", None), "objects", [])))
        object_count = len(getattr(getattr(app, "props", None), "objects", []))
        meshes = getattr(app, "meshes", max(1, object_count + 5))
        triangles = getattr(app, "triangles", max(8000, int(getattr(getattr(terrain, "mesh", None), "count", 0) / 3)))
        vertices = getattr(app, "vertices", max(1200, int(getattr(getattr(terrain, "mesh", None), "count", 0) * 0.75)))
        textures = getattr(app, "textures", 18)

        if player is not None and hasattr(player, "position"):
            px, py, pz = (float(player.position.x), float(player.position.y), float(player.position.z))
            speed = getattr(player, "speed", 0.0)
        else:
            px, py, pz = (0.0, 0.0, 0.0)
            speed = 0.0

        if camera is not None:
            yaw = float(getattr(camera, "yaw", 0.0))
            pitch = float(getattr(camera, "pitch", 0.0))
            cam_pos = getattr(camera, "position", glm.vec3(px, py, pz))
            cx, cy, cz = (float(cam_pos.x), float(cam_pos.y), float(cam_pos.z))
        else:
            yaw, pitch = 0.0, 0.0
            cx, cy, cz = px, py, pz

        if sun is not None and hasattr(sun, "direction"):
            sun_dir = sun.direction
            sun_elevation = math.degrees(math.asin(max(-1.0, min(1.0, float(sun_dir.y)))))
            sun_intensity = float(getattr(sun, "intensity", 0.0))
        else:
            sun_elevation = 0.0
            sun_intensity = 0.0

        if moon is not None:
            moon_intensity = float(getattr(moon, "intensity", 0.0))
        else:
            moon_intensity = 0.0

        if time_of_day is not None:
            time_hours = float(getattr(time_of_day, "current_time", 0.0))
        else:
            time_hours = 0.0

        if terrain is not None and hasattr(terrain, "height_at"):
            terrain_height = float(terrain.height_at(px, pz))
        else:
            terrain_height = 0.0

        ambient = getattr(app.lighting, "ambient", getattr(app, "ambient_light", 0.35)) if hasattr(app, "lighting") else 0.35
        opengl_version = glGetString(GL_VERSION).decode("utf-8", errors="ignore") if glGetString(GL_VERSION) else "Unknown"
        renderer = glGetString(GL_RENDERER).decode("utf-8", errors="ignore") if glGetString(GL_RENDERER) else "Unknown"

        return {
            "fps": float(fps),
            "frame_time": float(frame_time),
            "player_xyz": (px, py, pz),
            "camera_xyz": (cx, cy, cz),
            "yaw": yaw,
            "pitch": pitch,
            "looking": self._cardinal_direction(yaw),
            "world_name": world_name,
            "weather": weather,
            "time_of_day": time_hours,
            "time_label": self._format_time(time_hours),
            "day_number": int(day_number),
            "sun_elevation": float(sun_elevation),
            "sun_direction": getattr(sun, "direction", None),
            "sun_intensity": float(sun_intensity),
            "moon_intensity": float(moon_intensity),
            "ambient": float(ambient),
            "visible_objects": int(visible_objects),
            "meshes": int(meshes),
            "triangles": int(triangles),
            "vertices": int(vertices),
            "textures": int(textures),
            "terrain_height": float(terrain_height),
            "distance_from_origin": float(math.sqrt(px * px + py * py + pz * pz)),
            "speed": float(speed),
            "opengl_version": opengl_version,
            "renderer": renderer,
        }

    def _add_triangles(self, vertices, x, y, w, h, color):
        r, g, b, a = color
        vertices.extend([
            x, y, r, g, b, a,
            x + w, y, r, g, b, a,
            x, y + h, r, g, b, a,
            x + w, y, r, g, b, a,
            x + w, y + h, r, g, b, a,
            x, y + h, r, g, b, a,
        ])

    def _draw_text(self, vertices, x, y, text, color):
        cursor_x = float(x)
        for char in str(text):
            glyph = FONT_5X7.get(char.upper(), FONT_5X7[" "])
            for row_index, bits in enumerate(glyph):
                for col_index in range(5):
                    if bits & (1 << (4 - col_index)):
                        self._add_triangles(vertices, cursor_x + col_index * 1.35, y + row_index * 1.35, 1.2, 1.2, color)
            cursor_x += 6.0

    def draw_overlay(self, app):
        if not self.enabled or self.window_handle is None:
            return

        if not self.snapshot:
            self.snapshot = self.build_snapshot(app, 60.0, 0.016)

        width, height = glfw.get_window_size(self.window_handle)
        if width <= 0 or height <= 0:
            return

        snapshot = self.snapshot
        lines = [
            "C A S T A W A Y : B E Y O N D  T H E  S H O R E",
            f"FPS: {snapshot['fps']:.0f}",
            f"Frame: {snapshot['frame_time'] * 1000.0:.1f} ms",
            "",
            f"XYZ: {snapshot['player_xyz'][0]:.2f} / {snapshot['player_xyz'][1]:.2f} / {snapshot['player_xyz'][2]:.2f}",
            f"Yaw: {snapshot['yaw']:.1f}",
            f"Pitch: {snapshot['pitch']:.1f}",
            f"Looking: {snapshot['looking']}",
            f"Time: {snapshot['time_label']}",
            f"Day: {snapshot['day_number']}",
            "",
            f"Sun Elevation: {snapshot['sun_elevation']:.1f}°",
            f"Sun Intensity: {snapshot['sun_intensity']:.2f}",
            f"Moon Intensity: {snapshot['moon_intensity']:.2f}",
            f"Ambient: {snapshot['ambient']:.2f}",
            "",
            f"Objects: {snapshot['visible_objects']}",
            f"Meshes: {snapshot['meshes']}",
            f"Triangles: {snapshot['triangles']:,}",
            f"Vertices: {snapshot['vertices']:,}",
            f"Textures: {snapshot['textures']}",
            "",
            f"OpenGL: {snapshot['opengl_version']}",
            f"Renderer: {snapshot['renderer']}",
        ]

        panel_width = min(420, max(300, width // 3))
        panel_height = 18 + len(lines) * 14
        panel_x = 12
        panel_y = 12

        vertices = []
        self._add_triangles(vertices, panel_x, panel_y, panel_width, panel_height, (0.04, 0.06, 0.09, 0.72))

        color = (0.96, 0.96, 0.94, 1.0)
        cursor_y = panel_y + 14
        for line in lines:
            self._draw_text(vertices, panel_x + 12, cursor_y, line, color)
            cursor_y += 14

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, np.asarray(vertices, dtype=np.float32), GL_DYNAMIC_DRAW)
        self._hud_shader.use()
        self._hud_shader.set("uProjection", glm.ortho(0.0, float(width), float(height), 0.0, -1.0, 1.0))
        glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 6)
        glBindVertexArray(0)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    def info(self):
        return dict(self.snapshot)
