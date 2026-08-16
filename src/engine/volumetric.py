class VolumetricLighting:
    """World-space volumetric god-ray system driven by the sun and shadow map."""

    quality_profiles = {
        "LOW": {"steps": 12, "density": 0.22, "intensity": 0.55},
        "MEDIUM": {"steps": 20, "density": 0.18, "intensity": 0.7},
        "HIGH": {"steps": 28, "density": 0.14, "intensity": 0.9},
        "ULTRA": {"steps": 40, "density": 0.12, "intensity": 1.1},
    }

    def __init__(self, quality="HIGH"):
        self.enabled = True
        self.quality = quality
        self.profile = self.quality_profiles[quality]
        self.steps = self.profile["steps"]
        self.density = self.profile["density"]
        self.intensity = self.profile["intensity"]
        self.shadow_bias = 0.008

    def set_quality(self, quality):
        quality = quality.upper()
        if quality not in self.quality_profiles:
            raise ValueError(f"Unknown quality profile: {quality}")
        self.quality = quality
        self.profile = self.quality_profiles[quality]
        self.steps = self.profile["steps"]
        self.density = self.profile["density"]
        self.intensity = self.profile["intensity"]

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
