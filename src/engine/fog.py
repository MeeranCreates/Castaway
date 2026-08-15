from dataclasses import dataclass
from pyglm import glm


@dataclass
class FogSystem:
    """Atmospheric fog for distance-based visibility and atmosphere.
    
    This system creates physically-plausible fog that:
    - Blends objects into the atmosphere based on distance
    - Responds to time of day (warm at sunrise/sunset, cool at night)
    - Has configurable density and falloff
    - Works with the existing lighting system
    
    The fog uses exponential fog formula for smooth falloff:
        fog_factor = exp(-distance * density)
    
    Which creates a natural atmospheric appearance rather than a hard cutoff.
    """
    
    # Core fog parameters
    density: float = 0.018         # Base fog density (controls thickness)
    start_distance: float = 10.0   # Distance where fog starts appearing
    max_distance: float = 600.0    # Distance where fog is nearly opaque (>0.99)
    
    # Visual parameters
    color: glm.vec3 = glm.vec3(0.5, 0.6, 0.7)  # Base fog color (blended with sky)
    enabled: bool = True                         # Toggle fog on/off
    
    def __post_init__(self):
        self.color = glm.vec3(self.color.x, self.color.y, self.color.z)
    
    def calculate_fog_color(self, sky_bottom, sky_horizon, sky_top, daylight_factor):
        """Calculate fog color based on time of day and sky colors.
        
        Fog color transitions through the day:
        - Night: Deep blue-gray (from sky_bottom)
        - Sunrise/Sunset: Warm orange-tinted (warm transition)
        - Day: Light gray-blue (from sky_horizon)
        
        Args:
            sky_bottom: Sky color at bottom (night color)
            sky_horizon: Sky color at horizon (dawn/dusk blend)
            sky_top: Sky color at top (zenith)
            daylight_factor: 0.0 (night) to 1.0 (noon)
        
        Returns:
            Fog color as glm.vec3
        """
        # Fog color follows a path through the sky colors
        # At night: use sky_bottom (dark blue)
        # At sunrise/sunset: emphasize sky_horizon (orange/pink)
        # At day: use a blend of horizon and top (lighter)
        
        if daylight_factor < 0.5:
            # Night to sunrise: blend from night (sky_bottom) through dawn (sky_horizon)
            transition = daylight_factor * 2.0  # 0->1 as we go from night to mid-dawn
            return glm.mix(sky_bottom, sky_horizon, transition)
        else:
            # Sunrise to day: blend from dawn (sky_horizon) to day (lighter)
            transition = (daylight_factor - 0.5) * 2.0  # 0->1 as we go from mid-dawn to noon
            day_fog = glm.mix(sky_horizon, glm.vec3(0.6, 0.65, 0.75), transition)
            return day_fog
    
    def set_density(self, density):
        """Set fog density.
        
        Args:
            density: Fog density (higher = thicker fog)
                    Typical range: 0.005 (very light) to 0.05 (heavy)
        """
        self.density = max(0.0, float(density))
    
    def set_start_distance(self, start):
        """Set distance where fog begins to appear.
        
        Args:
            start: Distance in world units where fog starts
        """
        self.start_distance = max(0.0, float(start))
    
    def set_max_distance(self, max_dist):
        """Set distance where fog becomes nearly opaque.
        
        Args:
            max_dist: Distance in world units where fog is ~99% opaque
        """
        self.max_distance = max(self.start_distance + 10.0, float(max_dist))
    
    def set_color(self, color):
        """Set base fog color.
        
        Args:
            color: RGB color as glm.vec3 or tuple
        """
        self.color = glm.vec3(color[0], color[1], color[2])
    
    def enable(self):
        """Enable fog rendering."""
        self.enabled = True
    
    def disable(self):
        """Disable fog rendering."""
        self.enabled = False
    
    # Presets for different weather conditions
    @staticmethod
    def preset_clear():
        """Clear day with minimal fog."""
        return FogSystem(density=0.008, start_distance=15.0, max_distance=800.0)
    
    @staticmethod
    def preset_hazy():
        """Hazy day with moderate fog."""
        return FogSystem(density=0.018, start_distance=10.0, max_distance=600.0)
    
    @staticmethod
    def preset_foggy():
        """Foggy day with dense fog."""
        return FogSystem(density=0.035, start_distance=5.0, max_distance=300.0)
    
    @staticmethod
    def preset_misty_night():
        """Misty night with fog."""
        return FogSystem(density=0.025, start_distance=8.0, max_distance=400.0)
