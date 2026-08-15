# Sky System: Visual Color Palette & Day/Night Cycle

## Time-of-Day Color Progression

### Hour by Hour (24-Hour Cycle)

```
TIME    SUN HEIGHT   DAYLIGHT  SKY COLOR PALETTE
                     FACTOR    (Bottom → Horizon → Zenith)
─────   ───────────  ────────  ────────────────────────────────────────

00:00   Below -0.2   0.0%      (Very Dark)      (Navy)         (Black)
 ·      Midnight     Night     #020308 ─────→  #020308 ─────→ #020308
 ·

04:00   Rising       15%       (Dark Purple)    (Deep Orange)  (Dark Blue)
 ·      Pre-dawn     Twilight  #1a1a35 ─────→  #6b3d24 ─────→ #0a1d43
 ·

06:00   At horizon   40%       (Orange)         (Light Orange) (Lighter Blue)
 ·      Sunrise      Morning   #6b3d24 ─────→  #c98a60 ─────→ #2e5a7a
 ·

09:00   High up      70%       (Light Orange)   (Pale Yellow)  (Light Sky)
 ·      Morning      Late AM   #c98a60 ─────→  #f0d66b ─────→ #4a8cb8
 ·

12:00   Highest      100%      (Light Blue)     (Bright Blue)  (Bright Blue)
 ·      Noon        Daytime    #3d7a83 ─────→  #62a2d3 ─────→ #2e4d84
 ·

15:00   Starting     70%       (Light Blue)     (Light Orange) (Light Sky)
 ·      Afternoon   Late PM    #3d7a83 ─────→  #e8a860 ─────→ #4a8cb8
 ·

18:00   At horizon   40%       (Orange)         (Deep Orange)  (Dark Blue)
 ·      Sunset      Evening    #6b3d24 ─────→  #d96b3a ─────→ #1a3a52
 ·

20:00   Sinking      15%       (Dark Purple)    (Dark Orange)  (Navy)
 ·      Dusk        Twilight   #1a1a35 ─────→  #4a2818 ─────→ #0a1620
 ·

22:00   Deep below   0%        (Very Dark)      (Navy)         (Black)
 ·      Late night  Night      #020308 ─────→  #020308 ─────→ #020308
 ·

23:59   Below -0.2   0.0%      (Very Dark)      (Navy)         (Black)
        Midnight    Night      #020308 ─────→  #020308 ─────→ #020308

```

---

## Actual Color Values (From Code)

### Night (daylight_factor = 0.0)

```
Bottom Color (Horizon):  #020308 (RGB: 2,  3,   8)   - Very dark blue
Zenith Color (Top):      #030c1b (RGB: 3,  12,  27)  - Slightly lighter dark blue
Moon Ambient:            Soft blue glow on terrain
```

### Sunrise/Sunset (daylight_factor = 0.3-0.7)

```
Bottom → Horizon interpolation:
  Night (#020308) → Dawn (#e09680) → Day (#62a2d3)
  Gradual shift from deep blue through orange to light blue

Zenith stays relatively blue but lighter:
  #030c1b → (mixed toward) #2e4d84

Cloud colors:
  Bottom: #9eaec2 (cool gray)
  Top:    #e0e4f0 (very light with orange tint)
```

### Day (daylight_factor = 1.0)

```
Bottom Color (Horizon):  #62a2d3 (RGB: 98,  162, 211) - Bright blue
Zenith Color (Top):      #2e4d84 (RGB: 46,  77,  132) - Medium blue
Sun Glow:                #ffbf2d (RGB: 255, 191, 45)  - Warm yellow-orange
```

---

## Cloud Color Transitions

### Day Time (High Daylight Factor)

```
Cloud Top:     #e0e4f0  (Very bright white-blue)
Cloud Bottom:  #9eaec2  (Cool gray shadow)
Overall Effect: Bright, well-lit, high contrast shadow
```

### Sunset Time (Medium Daylight Factor)

```
Cloud Top:     #c89a5a  (Warm peachy-orange)
Cloud Bottom:  #a07050  (Darker warm orange)
Overall Effect: Glowing, backlit by sun, orange/amber hues
```

### Night Time (No Daylight)

```
Cloud Top:     #556a7a  (Dark cool blue-gray)
Cloud Bottom:  #3a444d  (Very dark blue-gray)
Overall Effect: Silhouetted clouds, subtle moon glow
```

---

## Visual Sky Zones

### The Sky Gradient Map

```
          ▲
          │
    100%  │    ZENITH ZONE (Top 55% of screen)
          │  ┌──────────────────────────────┐
          │  │  Deep Blue (Day)             │
          │  │  - Strongest blue            │
          │  │  - Least affected by sun     │
          │  │                              │
     50%  │  ├─────────────────────────────┤  TRANSITION ZONE
          │  │    Smooth gradient           │
          │  │    Zenith → Horizon          │
          │  │                              │
          │  │    Uses smoothstep()         │
          │  │    for soft blend            │
          │  │                              │
      0%  │  ├─────────────────────────────┤  HORIZON ZONE (Bottom 45%)
          │  │  Bright/Orange (Day)        │
          │  │  - Most affected by sun     │
          │  │  - Brightest colors         │
          │  │  - Sun glow added here      │
          │  └──────────────────────────────┘
          └─────────────────────────────────────►

```

---

## Color Harmony Rules

### Design Philosophy

The colors follow **real-world atmospheric physics**:

1. **Rayleigh Scattering**
   - Short wavelengths (blue) scatter more
   - Blue dominates at the top
   - Longer wavelengths (orange/red) at horizon

2. **Golden Hour**
   - Sun low on horizon = orange/pink light
   - Light passes through more atmosphere
   - Creates warm glow on clouds

3. **Nighttime**
   - No direct sunlight
   - Moon provides cool blue ambient
   - Clouds lit by moon glow

---

## Customizing Color Palette

### For a Warmer World

Edit `app.py` `sky_colors()`:

```python
dawn = glm.vec3(.95, .65, .50)  # More orange
day = glm.vec3(.48, .70, .90)   # Slightly warmer blue
zenith = glm.vec3(.10, .18, .35) # Deeper blue
```

### For a Cooler World

```python
dawn = glm.vec3(.75, .50, .40)  # Less saturated orange
day = glm.vec3(.28, .52, .82)   # Cooler blue (more cyan)
zenith = glm.vec3(.01, .05, .15) # Much darker top
```

### For a Sci-Fi Purple Sky

```python
dawn = glm.vec3(.80, .40, .70)  # Purple sunset
day = glm.vec3(.60, .50, .90)   # Purple-blue day
zenith = glm.vec3(.20, .10, .40) # Dark purple top
```

### For a Desert/Hot Climate

```python
dawn = glm.vec3(1.0, .70, .40)  # Very orange
day = glm.vec3(.60, .75, .95)   # Hot light blue
zenith = glm.vec3(.15, .25, .50) # Lighter blue top (haze)
```

---

## Sun Glow Effect Details

### Current Implementation

```glsl
float sunGlow = clamp((uSunDirection.y + 0.15) * 0.8, 0.0, 1.0);
color += vec3(1.0, 0.75, 0.45) * sunGlow * (1.0 - h) * 0.22;
```

### What Each Part Does

- `(uSunDirection.y + 0.15)` — Sun height, shifted up (twilight starts earlier)
- `* 0.8` — Reduce intensity
- `clamp(...)` — Keep between 0.0 and 1.0
- `vec3(1.0, 0.75, 0.45)` — Warm golden color
- `* (1.0 - h)` — Glow only at bottom (horizon), fades at top
- `* 0.22` — Overall glow intensity (reduce for subtle, increase for dramatic)

### To Make Sun Glow More Dramatic

```glsl
color += vec3(1.0, 0.75, 0.45) * sunGlow * (1.0 - h) * 0.45;  // 0.45 instead of 0.22
```

### To Make Sun Glow Subtle

```glsl
color += vec3(1.0, 0.75, 0.45) * sunGlow * (1.0 - h) * 0.10;  // 0.10 instead of 0.22
```

---

## Cloud Color Blending

### Default Cloud Top (Daylight)

```
#e0e4f0 = RGB(224, 228, 240)
Brightness: 90% (very light)
Saturation: 5% (almost white, very slightly blue)
```

### Default Cloud Bottom (Shadow)

```
#9eaec2 = RGB(158, 174, 194)
Brightness: 70% (medium)
Saturation: 10% (gray-blue)
Contrast: 20% darker than top
```

### Visual Effect

- Top lit by sun (bright, warm in sunset)
- Bottom in shadow (cool, gray)
- Creates 3D "puffy" cloud appearance

---

## Testing Transitions

### Manual Sky Cycle Test

```python
import time
import math

# In your main loop:
elapsed = time.time() - start_time
time_of_day = (elapsed / 300.0) % 1.0  # 5-minute cycle

angle = time_of_day * math.pi * 2
sun_x = math.cos(angle) * 0.8
sun_y = math.sin(angle) * 0.8

app.sun.set_direction(glm.vec3(sun_x, sun_y, 0.5))
app.moon.opposite_of(app.sun.direction)

# Watch sky cycle through all colors in 5 minutes
```

### Color Accuracy Check

- [ ] Night sky is very dark (not bright gray)
- [ ] Sunrise has pink/orange, not pure red
- [ ] Noon sky is bright blue (not dark)
- [ ] Sunset mirrors sunrise colors
- [ ] Transitions are smooth (no visible steps)
- [ ] Clouds glow during golden hour
- [ ] Clouds are bright white at noon
- [ ] Clouds are dark at night but slightly visible

---

## Performance Notes

### Color Calculation Cost

- Simple `glm.mix()` calls: negligible (~0.01 ms)
- Done CPU-side once per frame
- Passed to shader as uniforms

### Shader Evaluation Cost

- `smoothstep()` for gradient: ~1 GPU instruction per pixel
- `mix()` for blending: ~1 GPU instruction per pixel
- Total per pixel: ~5-10 instructions
- Very fast (10,000+ pixels per ms on modern GPUs)

### Optimization Opportunity

If needed, could pre-compute color gradient as 1D texture and lookup instead of calculating, but current method is already extremely fast.
