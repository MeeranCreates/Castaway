# Sky System: Quick Reference & Configuration Guide

## Usage Quick Start

### Adjusting Sky Appearance

#### Controlling Daytime (Sun Position)

```python
# In GameApp or from external script
import math
from pyglm import glm

# Create a time variable (0.0 = midnight, 1.0 = next midnight)
time_of_day = 0.5  # Noon

# Calculate sun angle based on time
angle = time_of_day * math.pi * 2  # Full circle rotation
sun_x = math.cos(angle) * 0.8
sun_y = math.sin(angle) * 0.8  # Y = height in sky

# Apply to sun
app.sun.set_direction(glm.vec3(sun_x, sun_y, 0.5))

# Moon automatically opposite
app.moon.opposite_of(app.sun.direction)
```

#### Adjusting Sky Colors

```python
# The sky_colors() method blends automatically, but you can customize:
# Edit the color values in app.py sky_colors() method

# Example: Make sunset more dramatic
dawn = glm.vec3(1.0, 0.6, 0.3)  # More orange
day = glm.vec3(0.3, 0.5, 0.9)   # Shift blue slightly

# Or make night darker
night = glm.vec3(0.01, 0.01, 0.03)  # Very dark blue
```

#### Controlling Clouds

```python
# Make clouds denser (more visible)
app.clouds.set_density(0.8)  # 0.0 = wispy, 1.0 = heavy coverage

# Make clouds higher/lower
app.clouds.set_height(120.0)  # Higher above player

# Make clouds drift faster
app.clouds.set_speed(0.25)  # 0.12 is default

# Change wind direction
app.clouds.set_wind(glm.vec2(0.5, 0.2))  # East-northeast wind

# Change cloud appearance (dawn colors)
app.clouds.color_top = glm.vec3(1.0, 0.85, 0.7)
app.clouds.color_bottom = glm.vec3(0.7, 0.6, 0.5)
```

---

## Preset Configurations

### Bright Noon

```python
app.sun.set_direction(glm.vec3(0.0, 0.95, 0.3))
app.sun.set_intensity(1.4)
app.clouds.set_density(0.3)  # Few clouds
```

### Golden Hour (Sunset)

```python
app.sun.set_direction(glm.vec3(0.8, 0.1, 0.5))
app.sun.set_intensity(1.2)
app.clouds.set_density(0.6)  # More clouds to glow
```

### Midnight

```python
app.sun.set_direction(glm.vec3(0.0, -0.95, 0.3))
app.moon.opposite_of(app.sun.direction)
app.clouds.set_density(0.4)  # Silhouetted clouds
```

### Stormy

```python
app.clouds.set_density(0.9)  # Heavy clouds
app.clouds.set_speed(0.4)    # Fast moving
app.clouds.set_height(60.0)  # Lower, closer
app.sun.set_intensity(0.6)   # Dimmed
```

---

## Rendering Pipeline Details

### When Sky Renders

- **After**: Shadow map generation
- **Before**: Terrain, objects, water
- **Depth test**: LEQUAL (sky depth = 1.0, behind everything)

### Blend Modes Used

- **Sky**: Opaque (alpha = 1.0)
- **Clouds**: Normal blending (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
- **Sun/Moon**: Additive blending (GL_SRC_ALPHA, GL_ONE) — creates glow

### Uniforms Sent Per Frame

```glsl
// Sky shader
uSunDirection (vec3)
uSkyBottom (vec3)
uSkyHorizon (vec3)
uSkyZenith (vec3)

// Cloud shader
uCloudDensity (float)
uCloudHeight (float)
uCloudOffset (vec2)
uCloudTopColor (vec3)
uCloudBottomColor (vec3)
uTime (float)
uSunDirection (vec3)

// Sun/Moon disks
uDirection (vec3)
```

---

## Common Issues & Solutions

### Problem: Sky looks flat/posterized

**Cause**: Hard color bands instead of smooth gradients  
**Solution**: Shaders already use `smoothstep()` for smooth blending. If still banding, increase FBO resolution.

### Problem: Clouds disappear at top of screen

**Cause**: Dome fade effect too aggressive  
**Solution**: Adjust `smoothstep(0.8, 1.5, ...)` in clouds.frag to `smoothstep(1.2, 1.8, ...)`

### Problem: Clouds always move same direction

**Cause**: Wind not being set  
**Solution**: Ensure `app.clouds.set_wind()` is called with desired direction

### Problem: Sun/moon not visible

**Cause**: Sun disk shaders may need rebuilding or uniforms not sent  
**Solution**: Check `render_world()` in app.py for sun_disk_shader binding

### Problem: Night is too bright

**Cause**: Moon ambient strength too high  
**Solution**: Reduce `app.moon.set_ambient_strength(0.1)` to something lower

---

## Performance Tuning

### For Lower-End GPUs

Reduce cloud quality:

```python
# Use simpler noise (fewer FBM layers)
# Edit clouds.frag: change "for (int i = 0; i < 5; ++i)" to "for (int i = 0; i < 3; ++i)"

# Or disable clouds entirely (comment out render_cloud in render_world)
```

### For High-End GPUs

Increase cloud quality:

```python
# Use more noise layers (slower but better quality)
# Edit clouds.frag: change loop to "for (int i = 0; i < 8; ++i)"

# Or add volumetric lighting to sun rays
```

---

## Extending the System

### Adding a Fog Effect

1. Add to `app.py`:

```python
def calculate_fog_density(self):
    # Fog thicker at night
    return 0.2 + 0.3 * (1.0 - self.sun.daylight_factor)

def apply_fog_uniform(self, shader):
    shader.set("uFogDensity", self.calculate_fog_density())
    shader.set("uFogColor", self.sky_colors()[0])  # Use sky bottom color
```

2. In terrain/water shaders:

```glsl
uniform float uFogDensity;
uniform vec3 uFogColor;

float fog = exp(-length(vWorldPos - uCameraPos) * uFogDensity);
fragColor.rgb = mix(uFogColor, fragColor.rgb, fog);
```

### Adding Stars

1. Create `src/engine/stars.py`:

```python
@dataclass
class StarField:
    stars: list = field(default_factory=list)
    brightness: float = 0.0  # 0 at day, 1 at night

    def update_brightness(self, daylight_factor):
        self.brightness = 1.0 - daylight_factor
```

2. Create `assets/shaders/stars.frag` to render star points

3. Add to render_world() after clouds:

```python
if self.stars.brightness > 0.01:
    self.stars_shader.use()
    self.stars_shader.set("uBrightness", self.stars.brightness)
    self.stars.draw()
```

---

## Architecture Notes

### Why This Design?

1. **Separation of Concerns**
   - Sun/Moon = Lighting data
   - Sky shader = Visual rendering
   - Clouds = Atmospheric layer
   - Each can be modified independently

2. **Modular Rendering**
   - Sky renders to screen-space quad (2D)
   - Clouds also screen-space but with 3D positioning
   - Sun/Moon are screen-space disks with glow
   - Allows future volumetric passes without restructuring

3. **Performance First**
   - No texture lookups (procedural noise in shader)
   - No complex math (linear interpolation and simple noise)
   - GPU-driven (all work on GPU, minimal CPU overhead)

4. **Extensible**
   - Time-of-day drives everything via sun direction
   - Any new effect can hook into sun/time data
   - New layers can insert between sky and scene without changing existing code

---

## Testing Checklist

- [ ] Sky transitions smoothly from night → dawn → day → dusk → night
- [ ] No visible color banding or posterization
- [ ] Clouds drift in wind direction
- [ ] Clouds denser during stormy settings
- [ ] Sun glow visible when sun is above horizon
- [ ] Moon visible when sun is below horizon
- [ ] Terrain lighting matches sky brightness
- [ ] Frame rate stays above 60 FPS with clouds enabled
- [ ] Changing density doesn't cause framerate spikes
- [ ] Sky colors match visual theme (not too fantasy-like)
