# Castaway renderer: Apple Silicon master guide

This starter targets the last desktop OpenGL API supplied by macOS: **OpenGL 4.1 Core**. It is intentionally not a compatibility-profile renderer and never depends on compute shaders, SSBOs, bindless textures, geometry shaders, or GLSL attribute `layout(location=...)` declarations. Those constraints keep it viable on Apple Silicon's native macOS OpenGL driver.

## Native setup (Apple Silicon)

Use an arm64 terminal. Homebrew's native prefix is normally `/opt/homebrew`; do not mix an Intel/Rosetta Python with arm64 GLFW.

```zsh
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python glfw pkg-config
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.main
```

If GLFW is not found at runtime, first confirm both Python and Homebrew are arm64:

```zsh
python -c "import platform; print(platform.machine())"
brew --prefix glfw
```

Both should report native arm64 paths/results. `PyOpenGL-accelerate` is optional but recommended for Python-to-driver call overhead. This project uses GLFW rather than Pygame because GLFW exposes macOS Core Profile and Cocoa/Retina controls explicitly.

## Non-negotiable macOS rules

`src/engine/window.py` requests major/minor `4.1`, `OPENGL_CORE_PROFILE`, and `OPENGL_FORWARD_COMPAT` **before** `glfw.create_window`. Forward compatibility is mandatory on macOS; omitting it is a frequent source of a null context or an immediate crash. `COCOA_RETINA_FRAMEBUFFER` is enabled, and rendering dimensions always come from `glfw.get_framebuffer_size`, never from the point-sized window dimensions.

Every shader in `assets/shaders` begins with exactly `#version 410 core`. Attribute locations are deliberately assigned with `glBindAttribLocation` during link, which avoids relying on GLSL `layout(location=...)`. Keep uniforms and sampler count modest, use UBOs only if a later profiling pass shows they are useful, and query extension availability rather than assuming a newer desktop GL feature exists.

## Render architecture

```text
terrain depth ──► GL_TEXTURE_2D depth FBO ─┐
                                           ├──► HDR RGBA16F FBO ──► fullscreen tone map ──► Retina framebuffer
terrain + PCF shadow + splat PBR-lite ─────┤
Gerstner water / instanced grass / sky ────┘
```

`GameApp` owns frame order and shared matrices. `Window`, `OrbitCamera`, `Shader`, `Mesh`, `Terrain`, `InstancedVegetation`, and the FBO classes each own one clear responsibility. It is safe to replace a module without spreading OpenGL state code through gameplay classes.

## Included systems

- **Third-person orbit camera:** right-mouse drag adjusts yaw/pitch; scroll adjusts distance. `glm.lookAt` and `glm.perspective` supply the view/projection matrices.
- **Playable island slice:** `WASD` moves the player in camera-relative directions. The player samples the exact terrain height function used to build the mesh and is constrained by colliders around trees and rocks. The visible orange player, trees, rocks, and shipwreck are genuine mesh objects in the scene and participate in the shadow pass.
- **Sun and soft shadows:** a 2048² depth `GL_TEXTURE_2D` FBO renders terrain from the directional light. The terrain fragment shader uses a 3×3 PCF comparison with slope-aware depth bias.
- **Terrain splatting:** a coherent island heightfield becomes a grid with central-difference normals and tangents. Grass, dirt, and rock use slope/height weights. The starter generates mipmapped sRGB terrain tiles procedurally, including ground variation; swap those for authored albedo/normal-map assets when ready.
- **Water:** three Gerstner components displace the water plane in the vertex stage. Its fragment shader combines animated ripple normal perturbation, Fresnel color shift, and high-power sun specular.
- **Vegetation:** a single blade mesh and `mat4` instance stream render thousands of instances with `glDrawElementsInstanced`. The matrix is passed as four attributes with divisor 1. Vertex-side sine wind avoids CPU animation upload.
- **Atmosphere/post:** a three-color-ready vertical sky gradient draws first; scene lighting goes to `RGBA16F`, then exponential tone mapping and gamma correction draw the display image.

## Production next steps

1. Replace the procedural textures with KTX2/PNG assets, generate mipmaps, and use sampler anisotropy only after checking its extension.
2. Partition terrain into chunks. Rebuild mesh data in a worker, but make all OpenGL calls on the context-owning render thread.
3. Add frustum/distance culling and split vegetation into cells before increasing the instance count. Keep static matrices in `GL_STATIC_DRAW`.
4. Profile in Xcode Instruments and capture representative scenes. On M1, reducing overdraw, resolution, texture traffic, and shadow-map redraws usually beats clever shader complexity.
5. Render transparent water after opaque terrain, with `glEnable(GL_BLEND)` / `glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)` and depth writes disabled for that pass. The starter keeps state simple so the individual systems are easy to study.

## Validation checklist

At startup, inspect `glGetString(GL_VERSION)` while developing: it should describe a 4.1 context. Resize the window on a Retina display: the viewport must follow the framebuffer pixel dimensions. Confirm no shader compiles with a GLSL version other than 410 core. Test right-drag, scroll, shadowed terrain, grass wind, and resized HDR target before adding gameplay systems.
