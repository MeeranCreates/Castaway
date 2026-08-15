import os
import glfw
import numpy as np
from pyglm import glm
from OpenGL.GL import *
from .window import Window
from .camera import OrbitCamera
from .shader import Shader
from .mesh import make_plane, make_box
from .terrain import Terrain
from .vegetation import InstancedVegetation
from .render_targets import ShadowMap, HdrTarget
from .player import Player
from .world import IslandProps, SceneObject


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHADERS = os.path.join(ROOT, "assets", "shaders")
ATTRS = {"aPosition": 0, "aNormal": 1, "aTangent": 2, "aUV": 3,
         "aInstance0": 4, "aInstance1": 5, "aInstance2": 6, "aInstance3": 7}


def shader(name, attrs=ATTRS):
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
        glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glEnable(GL_MULTISAMPLE); glEnable(GL_FRAMEBUFFER_SRGB)
        self.terrain, self.water = Terrain(), make_plane(180.0)
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
        self.albedo = [ground_texture(c, seed) for c, seed in (((52, 105, 38), 7), ((108, 103, 91), 11), ((104, 62, 31), 17))]
        self.normal = solid_texture(None, True)
        glfw.set_scroll_callback(self.window.handle, lambda _w, _x, y: self.camera.zoom(y))
        glfw.set_cursor_pos_callback(self.window.handle, lambda _w, x, y: self.camera.mouse_look(x, y, glfw.get_mouse_button(_w, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS))

    @staticmethod
    def bind_texture(unit, texture):
        glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, texture)

    def light_space(self):
        light_pos = glm.vec3(-52, 68, 34)
        return glm.ortho(-85, 85, -85, 85, 1, 180) * glm.lookAt(light_pos, glm.vec3(0), glm.vec3(0, 1, 0))

    def render_shadow(self, light_space):
        self.shadow.begin(); glCullFace(GL_FRONT)
        self.depth_shader.use(); self.depth_shader.set("uLightSpace", light_space); self.depth_shader.set("uModel", glm.mat4(1))
        self.terrain.mesh.draw()
        for obj in [*self.props.objects, self.player_visual]:
            self.depth_shader.set("uModel", obj.model); obj.mesh.draw()
        glCullFace(GL_BACK)

    def render_scene_objects(self, view, projection, light_space):
        s = self.scene_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", glm.normalize(glm.vec3(-.45, -.75, .35))),
                            ("uAmbientSky", glm.vec3(.24, .34, .43))): s.set(name, value)
        self.bind_texture(0, self.shadow.texture); s.set("uShadowMap", 0)
        self.player_visual.position = self.player.position + glm.vec3(0, .85, 0)
        self.player_visual.rotation = self.player.facing
        for obj in [*self.props.objects, self.player_visual]:
            s.set("uModel", obj.model); s.set("uColor", obj.color); obj.mesh.draw()

    def render_world(self, view, projection, light_space):
        self.sky_shader.use(); self.sky_shader.set("uView", glm.mat4(glm.mat3(view))); self.sky_shader.set("uProjection", projection)
        glDepthFunc(GL_LEQUAL); self.screen.draw(); glDepthFunc(GL_LESS)
        s = self.terrain_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uLightSpace", light_space),
                            ("uCameraPos", self.camera.position), ("uSunDirection", glm.normalize(glm.vec3(-.45, -.75, .35))),
                            ("uAmbientSky", glm.vec3(.24, .34, .43)), ("uRoughness", .72)): s.set(name, value)
        for unit, tex in enumerate(self.albedo): self.bind_texture(unit, tex); s.set("uAlbedo" + str(unit), unit)
        for unit in range(3, 6): self.bind_texture(unit, self.normal); s.set("uNormal" + str(unit - 3), unit)
        self.bind_texture(6, self.shadow.texture); s.set("uShadowMap", 6); self.terrain.mesh.draw()
        self.render_scene_objects(view, projection, light_space)
        s = self.grass_shader; s.use()
        for name, value in (("uView", view), ("uProjection", projection), ("uTime", self.time), ("uSunDirection", glm.vec3(-.45, -.75, .35))): s.set(name, value)
        glDisable(GL_CULL_FACE); self.vegetation.draw(); glEnable(GL_CULL_FACE)
        s = self.water_shader; s.use()
        for name, value in (("uModel", glm.mat4(1)), ("uView", view), ("uProjection", projection), ("uCameraPos", self.camera.position), ("uTime", self.time), ("uSunDirection", glm.vec3(-.45, -.75, .35))): s.set(name, value)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        self.water.draw(); glDepthMask(GL_TRUE); glDisable(GL_BLEND)

    def present(self, view):
        width, height = self.window.framebuffer_size
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glViewport(0, 0, width, height); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.post_shader.use(); self.bind_texture(0, self.hdr.color); self.bind_texture(1, self.hdr.depth); self.post_shader.set("uHdr", 0); self.post_shader.set("uDepth", 1); self.post_shader.set("uExposure", .88)
        self.post_shader.set("uFogColor", glm.vec3(.52, .63, .70)); self.screen.draw()

    def run(self):
        previous = glfw.get_time()
        while not self.window.should_close:
            now = glfw.get_time(); dt = min(now - previous, .1); self.time += dt; previous = now; glfw.poll_events()
            if glfw.get_key(self.window.handle, glfw.KEY_ESCAPE) == glfw.PRESS: glfw.set_window_should_close(self.window.handle, True)
            self.player.update(self.window.handle, self.camera, dt, self.props.colliders)
            self.camera.target = self.player.camera_target
            self.player_visual.position = self.player.position + glm.vec3(0, .85, 0)
            self.player_visual.rotation = self.player.facing
            width, height = self.window.framebuffer_size
            if (width, height) != (self.hdr.width, self.hdr.height): self.hdr.resize(width, height)
            aspect = width / max(height, 1)
            view, projection, light_space = self.camera.view(), self.camera.projection(aspect), self.light_space()
            self.render_shadow(light_space)
            glBindFramebuffer(GL_FRAMEBUFFER, self.hdr.fbo); glViewport(0, 0, width, height); glClearColor(.12, .18, .25, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render_world(view, projection, light_space); self.present(view); glfw.swap_buffers(self.window.handle)
        self.window.destroy()
