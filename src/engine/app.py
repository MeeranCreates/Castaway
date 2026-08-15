import os
import math
import glfw
import numpy as np
from pyglm import glm
from OpenGL.GL import *
from .window import Window
from .camera import OrbitCamera
from .shader import Shader
from .mesh import make_plane, make_box, make_sphere, make_cone
from .terrain import Terrain
from .vegetation import InstancedVegetation
from .render_targets import ShadowMap, HdrTarget
from .player import Player
from .world import IslandProps, SceneObject
from .sun import Sun
from .moon import Moon
from .clouds import CloudSystem
from .fog import FogSystem
from .time_of_day import TimeOfDay
from .lighting import LightingSystem
from .debug import DebugSystem


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHADERS = os.path.join(ROOT, "assets", "shaders")
ATTRS = {"aPosition": 0, "aNormal": 1, "aTangent": 2, "aUV": 3,
         "aInstance0": 4, "aInstance1": 5, "aInstance2": 6, "aInstance3": 7}


def shader(name, attrs=None):
    if attrs is None: attrs = ATTRS
    return Shader(os.path.join(SHADERS, name + ".vert"), os.path.join(SHADERS, name + ".frag"), attrs)


def solid_texture(rgb, normal=False):
    """Fallback procedural texture; swap this out for authored sRGB/PBR texture files."""
    tex = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex)
    pixel = np.array(([128, 128, 255] if normal else rgb), dtype=np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, pixel)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex


def ground_texture(base, seed):
    """Small mipmapped procedural albedo: a self-contained substitute for flat colour tiles."""
    rng, size = np.random.default_rng(seed), 128
    coarse = rng.normal(1.0, .10, (size, size, 1))
    specks = rng.random((size, size, 1))
    tint = np.asarray(base, dtype=np.float32).reshape(1, 1, 3)
    pixels = np.clip(tint * coarse + (specks > .965) * 12.0, 0, 255).astype(np.uint8)
    tex = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_SRGB8, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glGenerateMipmap(GL_TEXTURE_2D)
    return tex


class GameApp:
    def __init__(self):
        self.window = Window(); self.camera = OrbitCamera(); self.time = 0.0
        self.sun = Sun()
        self.moon = Moon()
        self.clouds = CloudSystem()
        self.fog = FogSystem()
        self.time_of_day = TimeOfDay(current_time=12.0)
        self.lighting = LightingSystem()
        self.world_name = "Seabreeze Isles"
        self.weather = "Clear"
        self.day_number = 1
        self.visible_objects = 0
        self.meshes = 0
        self.triangles = 0
        self.vertices = 0
        self.textures = 18
        self.debug = DebugSystem(self.window.handle)
        self.debug_point_mesh = make_sphere(0.18, 14, 8)
        self.debug_spot_mesh = make_cone(0.30, 0.85, 18)
        self.sync_day_night()
        glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glEnable(GL_MULTISAMPLE); glEnable(GL_FRAMEBUFFER_SRGB)
        self.terrain, self.water = Terrain(spacing=3.0), make_plane(1200.0)
        self.player = Player(self.terrain, glm.vec3(0, 0, 6))
        self.camera.target = self.player.camera_target
        self.props = IslandProps(self.terrain)
        self.player_visual = SceneObject(make_box(), self.player.position, glm.vec3(.7, 1.7, .7), glm.vec3(.75, .18, .08))
        self.vegetation, self.screen = InstancedVegetation(self.terrain), make_plane(2.0)
        self.shadow = ShadowMap(); self.hdr = HdrTarget(*self.window.framebuffer_size)
        self.depth_shader = shader("depth", {"aPosition": 0})
        self.terrain_shader, self.water_shader = shader("terrain"), shader("water")
        self.grass_shader, self.sky_shader, self.post_shader = shader("vegetation"), shader("sky", {"aPosition": 0}), shader("post", {"aPosition": 0})
        self.scene_shader = shader("scene")
        self.sun_disk_shader = shader("sun_disk", {"aPosition": 0, "aUV": 3})
        self.moon_disk_shader = shader("moon_disk", {"aPosition": 0, "aUV": 3})
        self.cloud_shader = shader("clouds", {"aPosition": 0, "aUV": 3})
        self.cloud_mesh = make_plane(1200.0)
        self.albedo = [ground_texture(c, seed) for c, seed in (((52, 105, 38), 7), ((108, 103, 91), 11), ((104, 62, 31), 17))]
        self.normal = solid_texture(None, True)
        glfw.set_input_mode(self.window.handle, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_scroll_callback(self.window.handle, lambda _w, _x, y: self.camera.zoom(y))
        glfw.set_cursor_pos_callback(self.window.handle, lambda _w, _x, _y: None)

    @staticmethod
    def bind_texture(unit, texture):
        glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, texture)

    def sync_day_night(self):
        state = self.time_of_day.apply_to(self.sun, self.moon, self.clouds, self.fog)
        self.lighting.update_from_cycle(state)
        return state

    def sun_direction(self):
        return self.sun.direction

    def sky_colors(self):
        state = self.sync_day_night()
        return state["sky_bottom"], state["sky_horizon"], state["sky_zenith"]

    def calculate_fog_color(self):
        """Calculate fog color based on the current cycle."""
        state = self.sync_day_night()
        return state["fog_color"]

    def apply_fog_uniforms(self, shader):
        """Apply fog uniforms to a shader."""
        shader.use()
        fog_color = self.calculate_fog_color()
        shader.set("uFogColor", fog_color)
        shader.set("uFogDensity", self.fog.density)
        shader.set("uFogStart", self.fog.start_distance)
        shader.set("uFogMax", self.fog.max_distance)
        shader.set("uDebugMode", 0)
        shader.set("uExposure", self.lighting.exposure)

    def set_debug_uniforms(self, shader):
        shader.use()
        shader.set("uDebugMode", 0)
        shader.set("uExposure", self.lighting.exposure)

    def light_space(self):
        light_pos = self.sun_direction() * 220.0 + glm.vec3(0, 90.0, 0)
        return glm.ortho(-290, 290, -290, 290, 1, 520) * glm.lookAt(light_pos, glm.vec3(0), glm.vec3(0, 1, 0))

    def apply_sun_uniforms(self, shader, view=None, projection=None, light_space=None):
        shader.use()
        shader.set("uSunDirection", self.sun.direction)
        shader.set("uSunColor", self.sun.color * self.sun.intensity)
        shader.set("uAmbientStrength", self.sun.ambient_strength)
        shader.set("uMoonDirection", self.moon.direction)
        shader.set("uMoonColor", self.moon.color * self.moon.intensity)
        shader.set("uMoonAmbientStrength", self.moon.ambient_strength)
        if view is not None: shader.set("uView", view)
        if projection is not None: shader.set("uProjection", projection)
        if light_space is not None: shader.set("uLightSpace", light_space)

    def apply_moon_uniforms(self, shader):
        shader.use()
        shader.set("uMoonDirection", self.moon.direction)
        shader.set("uMoonColor", self.moon.color * self.moon.intensity)
        shader.set("uMoonAmbientStrength", self.moon.ambient_strength)

    def render_shadow(self, light_space):
        self.shadow.begin(); glEnable(GL_POLYGON_OFFSET_FILL); glPolygonOffset(12.0, 24.0); glCullFace(GL_FRONT)
        self.depth_shader.use(); self.depth_shader.set("uLightSpace", light_space); self.depth_shader.set("uModel", glm.mat4(1))
        self.terrain.mesh.draw()
        for obj in [*self.props.objects, self.player_visual]:
            self.depth_shader.set("uModel", obj.model); obj.mesh.draw()
        glCullFace(GL_BACK); glDisable(GL_POLYGON_OFFSET_FILL)

    def render_scene_objects(self, view, projection, light_space):
        sun = self.sun_direction(); ambient = glm.mix(glm.vec3(.02, .03, .08), glm.vec3(.24, .34, .43), self.sun.daylight_factor)
        s = self.scene_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", sun),
                            ("uSunColor", self.sun.color * self.sun.intensity), ("uMoonDirection", self.moon.direction),
                            ("uMoonColor", self.moon.color * self.moon.intensity), ("uAmbientSky", ambient),
                            ("uAmbientStrength", self.sun.ambient_strength), ("uMoonAmbientStrength", self.moon.ambient_strength)): s.set(name, value)
        self.apply_fog_uniforms(s)
        self.lighting.build_shader_uniforms(s, self.camera.position, 0)
        self.bind_texture(0, self.shadow.texture); s.set("uShadowMap", 0)
        self.player_visual.position = self.player.position + glm.vec3(0, .85, 0)
        self.player_visual.rotation = self.player.facing
        for obj in [*self.props.objects, self.player_visual]:
            s.set("uModel", obj.model); s.set("uColor", obj.color); obj.mesh.draw()

    def render_world(self, view, projection, light_space):
        sun = self.sun_direction(); ambient = glm.mix(glm.vec3(.02, .03, .08), glm.vec3(.24, .34, .43), self.sun.daylight_factor)
        bottom, horizon, zenith = self.sky_colors()
        self.sky_shader.use(); self.sky_shader.set("uView", glm.mat4(glm.mat3(view))); self.sky_shader.set("uProjection", projection)
        self.sky_shader.set("uSunDirection", sun); self.sky_shader.set("uSkyBottom", bottom); self.sky_shader.set("uSkyHorizon", horizon); self.sky_shader.set("uSkyZenith", zenith)
        self.sky_shader.set("uDebugMode", 0); self.sky_shader.set("uExposure", self.lighting.exposure)
        glDepthFunc(GL_LEQUAL); self.screen.draw(); glDepthFunc(GL_LESS)

        self.cloud_shader.use();
        self.cloud_shader.set("uView", glm.mat4(glm.mat3(view)))
        self.cloud_shader.set("uProjection", projection)
        self.cloud_shader.set("uCloudOffset", self.clouds.offset)
        self.cloud_shader.set("uCloudDensity", self.clouds.density)
        self.cloud_shader.set("uCloudHeight", self.clouds.height)
        self.cloud_shader.set("uTime", self.time)
        self.cloud_shader.set("uSunDirection", sun)
        self.cloud_shader.set("uCloudTopColor", self.clouds.color_top)
        self.cloud_shader.set("uCloudBottomColor", self.clouds.color_bottom)
        self.cloud_shader.set("uDebugMode", 0)
        glDisable(GL_CULL_FACE); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        self.cloud_mesh.draw(); glDepthMask(GL_TRUE); glDisable(GL_BLEND); glEnable(GL_CULL_FACE)

        self.sun_disk_shader.use(); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        self.sun_disk_shader.set("uDirection", sun)
        self.screen.draw(); glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)

        self.moon_disk_shader.use(); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        self.moon_disk_shader.set("uDirection", self.moon.direction)
        self.screen.draw(); glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)

        # TERRAIN with fog
        s = self.terrain_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", sun), ("uSunColor", self.sun.color * self.sun.intensity),
                            ("uMoonDirection", self.moon.direction), ("uMoonColor", self.moon.color * self.moon.intensity),
                            ("uAmbientSky", ambient), ("uAmbientStrength", self.sun.ambient_strength), ("uMoonAmbientStrength", self.moon.ambient_strength),
                            ("uRoughness", .72)): s.set(name, value)
        self.apply_fog_uniforms(s)
        for unit, tex in enumerate(self.albedo): self.bind_texture(unit, tex); s.set("uAlbedo" + str(unit), unit)
        for unit in range(3, 6): self.bind_texture(unit, self.normal); s.set("uNormal" + str(unit - 3), unit)
        glDisable(GL_CULL_FACE)
        self.bind_texture(6, self.shadow.texture); s.set("uShadowMap", 6); self.terrain.mesh.draw()
        glEnable(GL_CULL_FACE)

        self.render_scene_objects(view, projection, light_space)
        
        # VEGETATION with fog
        s = self.grass_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uTime", self.time), ("uSunDirection", sun), ("uCameraPos", self.camera.position)): s.set(name, value)
        self.apply_fog_uniforms(s)
        self.lighting.build_shader_uniforms(s, self.camera.position)
        glDisable(GL_CULL_FACE); self.vegetation.draw(); glEnable(GL_CULL_FACE)

        # WATER with fog
        s = self.water_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uCameraPos", self.camera.position), ("uTime", self.time), ("uSunDirection", sun)): s.set(name, value)
        self.apply_fog_uniforms(s)
        self.lighting.build_shader_uniforms(s, self.camera.position)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        self.water.draw(); glDepthMask(GL_TRUE); glDisable(GL_BLEND); glEnable(GL_CULL_FACE)

    def present(self, view):
        width, height = self.window.framebuffer_size
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glViewport(0, 0, width, height); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        sun = self.sun_direction()
        fog_color = self.calculate_fog_color()
        self.post_shader.use(); self.bind_texture(0, self.hdr.color); self.bind_texture(1, self.hdr.depth)
        self.post_shader.set("uHdr", 0); self.post_shader.set("uDepth", 1); self.post_shader.set("uExposure", self.lighting.exposure)
        self.post_shader.set("uFogColor", fog_color); self.post_shader.set("uFogDensityPost", self.fog.density)
        self.post_shader.set("uDebugMode", 0)
        self.screen.draw()
        if self.debug.enabled:
            self.debug.draw_overlay(self)

    def run(self):
        previous = glfw.get_time()
        while not self.window.should_close:
            now = glfw.get_time(); dt = min(now - previous, .1); self.time += dt; previous = now; glfw.poll_events()
            if glfw.get_key(self.window.handle, glfw.KEY_ESCAPE) == glfw.PRESS: glfw.set_window_should_close(self.window.handle, True)
            self.debug.update(dt, self)
            self.time_of_day.advance(dt)
            self.sync_day_night()
            self.clouds.update(dt)
            width, height = self.window.framebuffer_size
            self.camera.update_from_locked_cursor(self.window.handle)
            self.player.update(self.window.handle, self.camera, dt, self.props.colliders)
            self.camera.follow_target(self.player.camera_target, dt, not self.player.grounded)
            self.player_visual.position = self.player.position + glm.vec3(0, .85, 0)
            self.player_visual.rotation = self.player.facing
            if (width, height) != (self.hdr.width, self.hdr.height): self.hdr.resize(width, height)
            aspect = width / max(height, 1)
            view, projection, light_space = self.camera.view(), self.camera.projection(aspect), self.light_space()
            self.render_shadow(light_space)
            glBindFramebuffer(GL_FRAMEBUFFER, self.hdr.fbo); glViewport(0, 0, width, height); glClearColor(.12, .18, .25, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render_world(view, projection, light_space)
            self.present(view); glfw.swap_buffers(self.window.handle)
        self.window.destroy()
