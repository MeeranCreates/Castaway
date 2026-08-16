from pathlib import Path
from src.engine.volumetric import VolumetricLighting


def test_volumetric_shader_has_shadow_aware_raymarching():
    shader = Path("assets/shaders/volumetric.frag").read_text()
    assert "uSceneDepth" in shader
    assert "uShadowMap" in shader
    assert "uSunDirection" in shader
    assert "for (int i = 0; i < MAX_STEPS; i++)" in shader or "for (int i = 0; i < 32; i++)" in shader


def test_volumetric_shader_has_moon_contribution():
    shader = Path("assets/shaders/volumetric.frag").read_text()
    assert "uMoonDirection" in shader
    assert "uMoonColor" in shader
    assert "uMoonIntensity" in shader


def test_volumetric_shader_has_complete_uniform_set():
    shader = Path("assets/shaders/volumetric.frag").read_text()
    required_uniforms = [
        "uSceneColor",
        "uSceneDepth",
        "uShadowMap",
        "uInvViewProjection",
        "uLightSpace",
        "uCameraPos",
        "uSunDirection",
        "uSunColor",
        "uSunIntensity",
        "uMoonDirection",
        "uMoonColor",
        "uMoonIntensity",
        "uResolution",
        "uFogDensity",
        "uVolumetricIntensity",
        "uShadowBias",
        "uQualitySteps",
    ]
    for uniform in required_uniforms:
        assert uniform in shader, f"Missing uniform: {uniform}"


def test_volumetric_system_exposes_quality_profiles():
    system = VolumetricLighting()
    assert system.quality_profiles["LOW"]["steps"] < system.quality_profiles["HIGH"]["steps"]
    assert system.quality_profiles["ULTRA"]["steps"] > system.quality_profiles["MEDIUM"]["steps"]


def test_volumetric_quality_settings_adjust_rendering_parameters():
    system = VolumetricLighting("LOW")
    low_steps = system.steps
    low_intensity = system.intensity
    
    system.set_quality("ULTRA")
    assert system.steps > low_steps
    assert system.intensity > low_intensity
    assert system.quality == "ULTRA"


def test_volumetric_can_be_enabled_and_disabled():
    system = VolumetricLighting()
    assert system.enabled is True
    
    system.set_enabled(False)
    assert system.enabled is False
    
    system.set_enabled(True)
    assert system.enabled is True


def test_volumetric_shadow_bias_is_configurable():
    system = VolumetricLighting()
    original_bias = system.shadow_bias
    system.shadow_bias = 0.016
    assert system.shadow_bias == 0.016
    assert system.shadow_bias != original_bias


def test_game_app_registers_time_cycle_and_volumetric_system():
    from src.engine.app import GameApp

    app = GameApp()
    assert hasattr(app, "time_of_day")
    assert hasattr(app, "volumetric")
    assert app.time_of_day.current_time >= 0.0


def test_moon_is_a_world_space_celestial_object():
    from src.engine.moon import Moon

    moon = Moon()
    assert hasattr(moon, "phase")
    assert hasattr(moon, "world_position")
    assert moon.world_position is not None


def test_moon_shader_supports_model_transform():
    shader = Path("assets/shaders/moon.vert").read_text()
    assert "uModel" in shader
    assert "uProjection * uView * uModel" in shader
