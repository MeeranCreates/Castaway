import math
from dataclasses import dataclass

from pyglm import glm


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


@dataclass
class TimeOfDay:
    """Single source of truth for the full Castaway day/night cycle.

    The cycle stores a continuous time in hours, then exposes smooth, interpolated
    values for the Sun, Moon, sky, fog, and clouds. This keeps gameplay time and
    rendering time independent while still making the renderer easy to extend for
    weather, storms, stars, and moon phases.
    """

    current_time: float = 12.0
    cycle_length: float = 24.0
    speed: float = 0.22
    sunrise_time: float = 6.0
    sunset_time: float = 18.0

    def __post_init__(self):
        self.current_time = float(self.current_time) % self.cycle_length

    def advance(self, dt):
        self.current_time = (self.current_time + dt * self.speed) % self.cycle_length

    def set_time(self, hours):
        self.current_time = float(hours) % self.cycle_length

    def _normalize_hour(self, hours=None):
        if hours is None:
            hours = self.current_time
        return float(hours) % self.cycle_length

    def _daylight_factor(self, hour):
        altitude = math.sin(((hour - self.sunrise_time) / max(1.0, self.sunset_time - self.sunrise_time)) * math.pi)
        return clamp01((altitude + 0.18) / 1.18)

    def _sun_direction_for(self, hour):
        theta = (hour / self.cycle_length) * math.tau - math.pi / 2.0
        pos = glm.vec3(math.cos(theta), math.sin(theta), math.sin(theta * 0.5))
        return glm.normalize(pos)

    def _moon_direction_for(self, sun_dir):
        return glm.normalize(-sun_dir + glm.vec3(0.0, 0.12, 0.0))

    def _sun_color_for_daylight(self, daylight):
        night = glm.vec3(0.38, 0.48, 0.8)
        dawn = glm.vec3(1.0, 0.70, 0.50)
        noon = glm.vec3(1.0, 0.94, 0.82)
        dusk = glm.vec3(1.0, 0.52, 0.38)

        if daylight < 0.2:
            return glm.mix(night, dawn, clamp01(daylight / 0.2))
        if daylight < 0.7:
            return glm.mix(dawn, noon, clamp01((daylight - 0.2) / 0.5))
        if daylight < 0.95:
            return glm.mix(noon, dusk, clamp01((daylight - 0.7) / 0.25))
        return glm.mix(dusk, night, clamp01((daylight - 0.95) / 0.05))

    def _sky_palette(self, daylight):
        night_bottom = glm.vec3(0.02, 0.03, 0.08)
        night_horizon = glm.vec3(0.04, 0.10, 0.18)
        night_zenith = glm.vec3(0.06, 0.12, 0.26)

        dawn_bottom = glm.vec3(0.45, 0.29, 0.25)
        dawn_horizon = glm.vec3(0.80, 0.56, 0.42)
        dawn_zenith = glm.vec3(0.17, 0.25, 0.48)

        day_bottom = glm.vec3(0.23, 0.37, 0.60)
        day_horizon = glm.vec3(0.36, 0.62, 0.82)
        day_zenith = glm.vec3(0.08, 0.16, 0.38)

        t = clamp01((daylight - 0.15) / 0.7)
        bottom = glm.mix(night_bottom, dawn_bottom, clamp01(daylight * 1.5))
        horizon = glm.mix(night_horizon, dawn_horizon, clamp01(daylight * 1.5))
        zenith = glm.mix(night_zenith, dawn_zenith, clamp01(daylight * 1.5))

        bottom = glm.mix(bottom, day_bottom, t)
        horizon = glm.mix(horizon, day_horizon, t)
        zenith = glm.mix(zenith, day_zenith, t)
        return bottom, horizon, zenith

    def _fog_params(self, daylight):
        fog_density = glm.mix(glm.vec3(0.032, 0.026, 0.022), glm.vec3(0.010, 0.012, 0.016), clamp01(daylight * 1.25))
        fog_color = glm.mix(glm.vec3(0.09, 0.12, 0.20), glm.vec3(0.75, 0.56, 0.44), clamp01(daylight * 1.5))
        fog_color = glm.mix(fog_color, glm.vec3(0.40, 0.45, 0.60), clamp01((daylight - 0.2) / 0.8))
        return fog_density.x, fog_color

    def _cloud_params(self, daylight):
        cloud_daylight = clamp01((daylight * 1.2) - 0.1)
        top = glm.mix(glm.vec3(0.56, 0.60, 0.68), glm.vec3(0.92, 0.94, 0.97), cloud_daylight)
        bottom = glm.mix(glm.vec3(0.32, 0.38, 0.48), glm.vec3(0.70, 0.75, 0.82), cloud_daylight)
        density = 0.42 + daylight * 0.38
        speed = 0.08 + daylight * 0.14
        lighting = 0.40 + daylight * 0.90
        return top, bottom, density, speed, lighting

    def evaluate_at(self, hours):
        hour = self._normalize_hour(hours)
        daylight = self._daylight_factor(hour)
        sun_dir = self._sun_direction_for(hour)
        moon_dir = self._moon_direction_for(sun_dir)

        sun_intensity = 0.08 + daylight * 1.25
        moon_intensity = 0.10 + (1.0 - daylight) * 0.85

        sky_bottom, sky_horizon, sky_zenith = self._sky_palette(daylight)
        fog_density, fog_color = self._fog_params(daylight)
        cloud_top, cloud_bottom, cloud_density, cloud_speed, cloud_lighting = self._cloud_params(daylight)

        return {
            "time": hour,
            "daylight": daylight,
            "sun_direction": sun_dir,
            "sun_color": self._sun_color_for_daylight(daylight),
            "sun_intensity": sun_intensity,
            "moon_direction": moon_dir,
            "moon_color": glm.vec3(0.62, 0.70, 0.98),
            "moon_intensity": moon_intensity,
            "sky_bottom": sky_bottom,
            "sky_horizon": sky_horizon,
            "sky_zenith": sky_zenith,
            "fog_density": fog_density,
            "fog_color": fog_color,
            "cloud_top_color": cloud_top,
            "cloud_bottom_color": cloud_bottom,
            "cloud_density": cloud_density,
            "cloud_speed": cloud_speed,
            "cloud_lighting": cloud_lighting,
            "ambient": glm.mix(glm.vec3(0.02, 0.03, 0.08), glm.vec3(0.22, 0.30, 0.42), daylight),
        }

    def evaluate(self):
        return self.evaluate_at(self.current_time)

    def apply_to(self, sun, moon, clouds, fog):
        state = self.evaluate()
        sun.set_direction(state["sun_direction"])
        sun.set_color(state["sun_color"])
        sun.set_intensity(state["sun_intensity"])
        sun.set_ambient_strength(0.17 + state["daylight"] * 0.40)

        moon.set_direction(state["moon_direction"])
        moon.set_color(state["moon_color"])
        moon.set_intensity(state["moon_intensity"])
        moon.set_ambient_strength(0.12 + (1.0 - state["daylight"]) * 0.28)

        clouds.set_density(state["cloud_density"])
        clouds.set_speed(state["cloud_speed"])
        clouds.color_top = state["cloud_top_color"]
        clouds.color_bottom = state["cloud_bottom_color"]

        fog.set_density(state["fog_density"])
        fog.set_color(state["fog_color"])
        return state
