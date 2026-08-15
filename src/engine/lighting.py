import math
from dataclasses import dataclass, field

from pyglm import glm


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def color_temperature_to_rgb(temperature):
    """Approximate black-body color for a given Kelvin value.

    This is a practical approximation used to keep the Sun and Moon colors tied to
    physically-inspired temperature ranges instead of arbitrary hand-picked RGBs.
    """
    temp = max(1000.0, min(40000.0, float(temperature)))

    if temp <= 66.0:
        r = 255.0
        g = temp
        g = 99.4708025861 * math.log(g) - 161.1195681661
    else:
        r = 329.698727446 * math.pow(temp - 60.0, -0.1332047592)
        g = 288.1221695283 * math.pow(temp - 60.0, -0.0755148492)

    if temp <= 66.0:
        b = temp
        b = 138.5177312231 * math.log(b - 10.0) - 305.0447927307
    else:
        b = 255.0

    r = clamp01(r / 255.0)
    g = clamp01(g / 255.0)
    b = clamp01(b / 255.0)
    return glm.vec3(r, g, b)


@dataclass
class DirectionalLight:
    """Physically inspired directional sunlight/mood light."""
    direction: glm.vec3 = glm.vec3(-0.65, 0.82, 0.32)
    color: glm.vec3 = glm.vec3(1.0, 0.9, 0.78)
    intensity: float = 1.0
    color_temperature: float = 6500.0
    angular_size: float = 0.55
    softness: float = 0.08
    enabled: bool = True

    def __post_init__(self):
        self.direction = glm.normalize(self.direction)

    @property
    def radiance(self):
        return self.color * self.intensity

    def set_direction(self, direction):
        self.direction = glm.normalize(direction)

    def set_color(self, color):
        self.color = glm.vec3(color.x, color.y, color.z)

    def set_intensity(self, intensity):
        self.intensity = max(0.0, float(intensity))

    def set_temperature(self, kelvin):
        self.color_temperature = float(kelvin)
        self.color = color_temperature_to_rgb(self.color_temperature)


@dataclass
class PointLight:
    position: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)
    color: glm.vec3 = glm.vec3(1.0, 0.6, 0.3)
    intensity: float = 1.0
    range: float = 12.0
    radius: float = 0.2
    enabled: bool = True

    @property
    def radiance(self):
        return self.color * self.intensity


@dataclass
class SpotLight:
    position: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)
    direction: glm.vec3 = glm.vec3(0.0, -1.0, 0.0)
    color: glm.vec3 = glm.vec3(1.0, 0.75, 0.5)
    intensity: float = 1.5
    range: float = 18.0
    inner_cone: float = 0.9
    outer_cone: float = 0.8
    enabled: bool = True

    def __post_init__(self):
        self.direction = glm.normalize(self.direction)


@dataclass
class Material:
    base_color: glm.vec3 = glm.vec3(0.8, 0.8, 0.8)
    roughness: float = 0.7
    metallic: float = 0.0
    ao: float = 1.0
    emissive: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)


@dataclass
class EnvironmentLighting:
    sky_bottom: glm.vec3 = glm.vec3(0.02, 0.03, 0.08)
    sky_horizon: glm.vec3 = glm.vec3(0.36, 0.62, 0.82)
    sky_top: glm.vec3 = glm.vec3(0.08, 0.16, 0.38)
    exposure: float = 1.0
    gamma: float = 2.2
    ambient_strength: float = 0.35
    irradiance_scale: float = 0.8


@dataclass
class LightingSystem:
    """Central lighting controller for the real-time engine.

    This is a practical real-time approximation of real-world light: directional
    sunlight, moonlight, sky lighting, atmospheric fog response, and support for
    local point and spot lights. It is not a full path tracer, but it uses a PBR-inspired
    model with directional light, ambient response, roughness, metallic response,
    and specular Fresnel terms.
    """

    sun: DirectionalLight = field(default_factory=lambda: DirectionalLight())
    moon: DirectionalLight = field(default_factory=lambda: DirectionalLight(direction=glm.vec3(-0.6, 0.7, -0.3), color=glm.vec3(0.6, 0.72, 0.96), intensity=0.18, color_temperature=6500.0))
    environment: EnvironmentLighting = field(default_factory=EnvironmentLighting)
    point_lights: list = field(default_factory=list)
    spot_lights: list = field(default_factory=list)
    exposure: float = 1.05
    gamma: float = 2.2
    shadow_bias: float = 0.0045
    shadow_filter_radius: float = 1.0

    def __post_init__(self):
        self.clear_point_lights()
        self.clear_spot_lights()

    def clear_point_lights(self):
        self.point_lights = []

    def clear_spot_lights(self):
        self.spot_lights = []

    def update_from_cycle(self, time_state):
        daylight = float(time_state["daylight"])

        self.sun.direction = glm.normalize(time_state["sun_direction"])
        self.sun.color = glm.vec3(time_state["sun_color"].x, time_state["sun_color"].y, time_state["sun_color"].z)
        self.sun.intensity = max(0.05, float(time_state["sun_intensity"]))
        self.sun.set_temperature(2800.0 + daylight * 5200.0)

        self.moon.direction = glm.normalize(time_state["moon_direction"])
        self.moon.color = glm.vec3(time_state["moon_color"].x, time_state["moon_color"].y, time_state["moon_color"].z)
        self.moon.intensity = max(0.0, float(time_state["moon_intensity"]))

        self.environment.sky_bottom = glm.vec3(time_state["sky_bottom"].x, time_state["sky_bottom"].y, time_state["sky_bottom"].z)
        self.environment.sky_horizon = glm.vec3(time_state["sky_horizon"].x, time_state["sky_horizon"].y, time_state["sky_horizon"].z)
        self.environment.sky_top = glm.vec3(time_state["sky_zenith"].x, time_state["sky_zenith"].y, time_state["sky_zenith"].z)
        self.environment.ambient_strength = 0.08 + daylight * 0.75
        self.environment.irradiance_scale = 0.45 + daylight * 0.9
        self.environment.exposure = self.exposure
        self.environment.gamma = self.gamma

        return self

    def environment_ambient(self):
        return glm.mix(self.environment.sky_bottom, self.environment.sky_horizon, 0.6) * self.environment.ambient_strength

    def add_point_light(self, light):
        self.point_lights.append(light)

    def add_spot_light(self, light):
        self.spot_lights.append(light)

    def build_shader_uniforms(self, shader, camera_pos, shadow_map=None):
        shader.use()
        shader.set("uExposure", self.exposure)
        shader.set("uGamma", self.gamma)
        shader.set("uCameraPos", camera_pos)
        shader.set("uAmbientSky", self.environment_ambient())
        shader.set("uSunDirection", self.sun.direction)
        shader.set("uSunColor", self.sun.radiance)
        shader.set("uSunIntensity", self.sun.intensity)
        shader.set("uMoonDirection", self.moon.direction)
        shader.set("uMoonColor", self.moon.radiance)
        shader.set("uMoonIntensity", self.moon.intensity)
        shader.set("uAmbientStrength", self.environment.ambient_strength)
        if shadow_map is not None:
            shader.set("uShadowMap", shadow_map)

    def describe(self):
        return {
            "sun": {
                "direction": self.sun.direction,
                "color": self.sun.color,
                "intensity": self.sun.intensity,
                "temperature": self.sun.color_temperature,
            },
            "moon": {
                "direction": self.moon.direction,
                "color": self.moon.color,
                "intensity": self.moon.intensity,
            },
            "environment": {
                "ambient": self.environment_ambient(),
                "exposure": self.exposure,
            },
        }
