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
from .world import IslandProps, SceneObject, TreeSystem
from .lighting import LightingSystem
from .time_of_day import TimeOfDay, clamp01
from .moon import Moon
from .sun import Sun
from .volumetric import VolumetricLighting
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
        self.time_of_day = TimeOfDay(current_time=12.0)
        self.lighting = LightingSystem()
        self.sun = self.lighting.sun
        self.moon = self.lighting.moon
        self.world_name = "Seabreeze Isles"
        self.weather = "Clear"
        self.day_number = 1
        self.debug = DebugSystem(self.window.handle)
        glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glEnable(GL_MULTISAMPLE); glEnable(GL_FRAMEBUFFER_SRGB)
        self.terrain, self.water = Terrain(spacing=3.0), make_plane(1200.0)
        self.props = IslandProps(self.terrain)
        self.tree_system = TreeSystem(self.terrain)
        self.player = Player(self.terrain, glm.vec3(0, 0, 6), trees=self.tree_system.trees)
        self.camera.target = self.player.camera_target
        self.vegetation, self.screen = InstancedVegetation(self.terrain), make_plane(2.0)
        self.shadow = ShadowMap(); self.hdr = HdrTarget(*self.window.framebuffer_size)
        self.volumetric = VolumetricLighting()
        self.volumetric_target = HdrTarget(*self.window.framebuffer_size)
        self.sun_object = Sun()
        self.celestial_moon = Moon()
        self.depth_shader = shader("depth", {"aPosition": 0})
        self.terrain_shader, self.water_shader = shader("terrain"), shader("water")
        self.grass_shader, self.post_shader = shader("vegetation"), shader("post", {"aPosition": 0})
        self.scene_shader = shader("scene")
        self.tree_shader = shader("trees")
        self.sun_shader = shader("sun")
        self.moon_shader = shader("moon")
        self.stars_shader = shader("stars")
        self.volumetric_shader = shader("volumetric", {"aPosition": 0})
        self.sun_mesh = make_sphere(12.0, segments=24, rings=16)
        self.moon_mesh = make_sphere(12.0, segments=24, rings=16)
        self.albedo = [ground_texture(c, seed) for c, seed in (((52, 105, 38), 7), ((108, 103, 91), 11), ((104, 62, 31), 17))]
        self.normal = solid_texture(None, True)
        glfw.set_input_mode(self.window.handle, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_scroll_callback(self.window.handle, lambda _w, _x, y: self.camera.zoom(y))
        glfw.set_cursor_pos_callback(self.window.handle, lambda _w, _x, _y: None)
        self.lighting.update_from_cycle(self.time_of_day.evaluate())

    @staticmethod
    def bind_texture(unit, texture):
        glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, texture)

    def sun_direction(self):
        return self.lighting.sun.direction if self.lighting is not None else glm.normalize(glm.vec3(0.65, 0.85, 0.35))

    def light_space(self):
        sun_dir = self.sun_direction(); light_pos = -sun_dir * 220.0 + glm.vec3(0, 90.0, 0)
        return glm.ortho(-290, 290, -290, 290, 1, 520) * glm.lookAt(light_pos, glm.vec3(0), glm.vec3(0, 1, 0))

    def apply_fog_uniforms(self, shader):
        """Apply fog uniforms to a shader."""
        shader.use()
        shader.set("uFogColor", glm.vec3(0.5, 0.6, 0.7))
        shader.set("uFogDensity", 0.0)
        shader.set("uFogStart", 10.0)
        shader.set("uFogMax", 600.0)
        shader.set("uDebugMode", 0)
        shader.set("uExposure", self.lighting.exposure)

    def render_shadow(self, light_space):
        self.shadow.begin(); glEnable(GL_POLYGON_OFFSET_FILL); glPolygonOffset(12.0, 24.0); glCullFace(GL_FRONT)
        self.depth_shader.use(); self.depth_shader.set("uLightSpace", light_space); self.depth_shader.set("uModel", glm.mat4(1))
        self.terrain.mesh.draw()
        for obj in [*self.props.objects, *self.tree_system.render_objects()]:
            self.depth_shader.set("uModel", obj.model); obj.mesh.draw()
        self.depth_shader.set("uModel", self.player.visual.model); self.player.visual.mesh.draw()
        glCullFace(GL_BACK); glDisable(GL_POLYGON_OFFSET_FILL)

    def render_scene_objects(self, view, projection, light_space):
        sun = self.sun_direction(); ambient = glm.vec3(0.24, 0.34, 0.43)
        s = self.scene_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", sun),
                            ("uSunColor", glm.vec3(1.0, 0.94, 0.82)), ("uMoonDirection", glm.vec3(0, 0, 0)),
                            ("uMoonColor", glm.vec3(0.6, 0.72, 0.96)), ("uAmbientSky", ambient),
                            ("uAmbientStrength", 0.35), ("uMoonAmbientStrength", 0.0)): s.set(name, value)
        self.apply_fog_uniforms(s)
        self.bind_texture(0, self.shadow.texture); s.set("uShadowMap", 0)
        for obj in self.props.objects:
            s.set("uModel", obj.model); s.set("uColor", obj.color); obj.mesh.draw()

        t = self.tree_shader; t.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", sun),
                            ("uSunColor", glm.vec3(1.0, 0.94, 0.82)), ("uAmbientSky", ambient),
                            ("uAmbientStrength", 0.35), ("uMoonAmbientStrength", 0.0),
                            ("uFogColor", glm.vec3(0.5, 0.6, 0.7)), ("uFogDensity", 0.0),
                            ("uFogStart", 10.0), ("uFogMax", 600.0)):
            t.set(name, value)
        self.bind_texture(0, self.shadow.texture); t.set("uShadowMap", 0)
        for obj in self.tree_system.render_objects():
            t.set("uModel", obj.model); t.set("uColor", obj.color); obj.mesh.draw()

        s.set("uModel", self.player.visual.model); s.set("uColor", self.player.visual.color); self.player.visual.mesh.draw()

    def render_world(self, view, projection, light_space):
        sun = self.sun_direction(); ambient = glm.vec3(0.24, 0.34, 0.43)
        s = self.terrain_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", sun), ("uSunColor", glm.vec3(1.0, 0.94, 0.82)),
                            ("uMoonDirection", glm.vec3(0, 0, 0)), ("uMoonColor", glm.vec3(0.6, 0.72, 0.96)),
                            ("uAmbientSky", ambient), ("uAmbientStrength", 0.35), ("uMoonAmbientStrength", 0.0),
                            ("uRoughness", .72)): s.set(name, value)
        self.apply_fog_uniforms(s)
        for unit, tex in enumerate(self.albedo): self.bind_texture(unit, tex); s.set("uAlbedo" + str(unit), unit)
        for unit in range(3, 6): self.bind_texture(unit, self.normal); s.set("uNormal" + str(unit - 3), unit)
        glDisable(GL_CULL_FACE)
        self.bind_texture(6, self.shadow.texture); s.set("uShadowMap", 6); self.terrain.mesh.draw()
        glEnable(GL_CULL_FACE)
        self.render_scene_objects(view, projection, light_space)
        s = self.grass_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uTime", self.time), ("uSunDirection", sun), ("uCameraPos", self.camera.position)): s.set(name, value)
        self.apply_fog_uniforms(s)
        glDisable(GL_CULL_FACE); self.vegetation.draw(); glEnable(GL_CULL_FACE)
        s = self.water_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uCameraPos", self.camera.position), ("uTime", self.time), ("uSunDirection", sun)): s.set(name, value)
        self.apply_fog_uniforms(s)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        self.water.draw(); glDepthMask(GL_TRUE); glDisable(GL_BLEND); glEnable(GL_CULL_FACE)

    def render_volumetric(self, view, projection, light_space):
        if not self.volumetric.enabled:
            return
        width, height = self.window.framebuffer_size
        if (width, height) != (self.volumetric_target.width, self.volumetric_target.height):
            self.volumetric_target.resize(width, height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.volumetric_target.fbo)
        glViewport(0, 0, width, height)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.volumetric_shader.use()
        self.bind_texture(0, self.hdr.color); self.volumetric_shader.set("uSceneColor", 0)
        self.bind_texture(1, self.hdr.depth); self.volumetric_shader.set("uSceneDepth", 1)
        self.bind_texture(2, self.shadow.texture); self.volumetric_shader.set("uShadowMap", 2)

        inv_view_proj = glm.inverse(projection * view)
        state = self.time_of_day.evaluate()
        self.volumetric_shader.set("uInvViewProjection", inv_view_proj)
        self.volumetric_shader.set("uCameraPos", self.camera.position)
        self.volumetric_shader.set("uSunDirection", self.lighting.sun.direction)
        self.volumetric_shader.set("uSunColor", self.lighting.sun.radiance)
        self.volumetric_shader.set("uSunIntensity", self.lighting.sun.intensity)
        self.volumetric_shader.set("uMoonDirection", self.lighting.moon.direction)
        self.volumetric_shader.set("uMoonColor", self.lighting.moon.radiance)
        self.volumetric_shader.set("uMoonIntensity", self.lighting.moon.intensity)
        self.volumetric_shader.set("uFogDensity", float(state["fog_density"]))
        self.volumetric_shader.set("uVolumetricIntensity", self.volumetric.intensity)
        self.volumetric_shader.set("uShadowBias", self.lighting.shadow_bias)
        self.volumetric_shader.set("uLightSpace", light_space)
        self.volumetric_shader.set("uResolution", glm.vec2(float(width), float(height)))
        self.volumetric_shader.set("uQualitySteps", self.volumetric.steps)
        self.screen.draw()

    def render_sun(self, view, projection):
        state = self.time_of_day.evaluate()
        sun_dir = glm.normalize(state["sun_direction"])
        sun_pos = sun_dir * 170.0 + glm.vec3(0, 60.0, 0)
        model = glm.translate(glm.mat4(1.0), sun_pos)
        for i in range(3):
            model[i][i] = 14.0
        self.sun_shader.use()
        self.sun_shader.set("uView", view)
        self.sun_shader.set("uProjection", projection)
        self.sun_shader.set("uModel", model)
        self.sun_shader.set("uSunDirection", sun_dir)
        self.sun_shader.set("uSunColor", state["sun_color"])
        self.sun_shader.set("uTime", self.time)
        self.sun_mesh.draw()

    def render_stars(self, view, projection):
        state = self.time_of_day.evaluate()
        star_visibility = clamp01(1.0 - state["daylight"]) * 1.5
        if star_visibility <= 0.01:
            return
        self.stars_shader.use()
        self.stars_shader.set("uView", view)
        self.stars_shader.set("uProjection", projection)
        self.stars_shader.set("uModel", glm.mat4(1.0))
        self.stars_shader.set("uTime", self.time)
        self.stars_shader.set("uNightFactor", star_visibility)
        self.sun_mesh.draw()

    def render_moon(self, view, projection):
        state = self.time_of_day.evaluate()
        self.celestial_moon.update_from_state(state["moon_direction"], state["sun_direction"])
        self.celestial_moon.visible = state["moon_intensity"] > 0.02
        if not self.celestial_moon.visible:
            return

        self.moon_shader.use()
        self.moon_shader.set("uView", view)
        self.moon_shader.set("uProjection", projection)
        self.moon_shader.set("uModel", self.celestial_moon.model_matrix())
        self.moon_shader.set("uSunDirection", state["sun_direction"])
        self.moon_shader.set("uMoonColor", self.celestial_moon.color)
        self.moon_shader.set("uMoonIntensity", self.celestial_moon.intensity)
        self.moon_shader.set("uPhase", self.celestial_moon.phase)
        self.moon_mesh.draw()

    def present(self, view):
        width, height = self.window.framebuffer_size
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glViewport(0, 0, width, height); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.post_shader.use(); self.bind_texture(0, self.hdr.color); self.bind_texture(1, self.volumetric_target.color); self.bind_texture(2, self.hdr.depth)
        self.post_shader.set("uHdr", 0); self.post_shader.set("uVolumetric", 1); self.post_shader.set("uDepth", 2); self.post_shader.set("uExposure", self.lighting.exposure)
        self.post_shader.set("uFogColor", glm.vec3(0.5, 0.6, 0.7)); self.post_shader.set("uFogDensityPost", 0.0)
        self.post_shader.set("uDebugMode", 0); self.post_shader.set("uVolumetricEnabled", 1 if self.volumetric.enabled else 0)
        self.screen.draw()
        if self.debug.enabled:
            self.debug.draw_overlay(self)

    def run(self):
        previous = glfw.get_time()
        while not self.window.should_close:
            now = glfw.get_time(); dt = min(now - previous, .1); self.time += dt; previous = now; glfw.poll_events()
            if glfw.get_key(self.window.handle, glfw.KEY_ESCAPE) == glfw.PRESS: glfw.set_window_should_close(self.window.handle, True)
            self.debug.update(dt, self)
            self.tree_system.update(dt)
            self.time_of_day.advance(dt)
            self.lighting.update_from_cycle(self.time_of_day.evaluate())
            self.sun = self.lighting.sun
            self.moon = self.lighting.moon
            width, height = self.window.framebuffer_size
            self.camera.update_from_locked_cursor(self.window.handle)
            self.player.update(self.window.handle, self.camera, dt, self.props.colliders + self.tree_system.colliders, self.tree_system.trees)
            self.camera.follow_target(self.player.camera_target, dt, not self.player.grounded)
            self.player.visual.update_from_player(self.player)
            if (width, height) != (self.hdr.width, self.hdr.height): self.hdr.resize(width, height)
            if (width, height) != (self.volumetric_target.width, self.volumetric_target.height): self.volumetric_target.resize(width, height)
            aspect = width / max(height, 1)
            view, projection, light_space = self.camera.view(), self.camera.projection(aspect), self.light_space()
            self.render_shadow(light_space)
            glBindFramebuffer(GL_FRAMEBUFFER, self.hdr.fbo); glViewport(0, 0, width, height); glClearColor(.12, .18, .25, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render_world(view, projection, light_space)
            self.render_stars(view, projection)
            self.render_sun(view, projection)
            self.render_moon(view, projection)
            self.render_volumetric(view, projection, light_space)
            self.present(view); glfw.swap_buffers(self.window.handle)
        self.window.destroy()
