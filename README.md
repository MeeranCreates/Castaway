# 🏝️ Castaway: Beyond the Shore

> *The island isn't waiting to be found. It's waiting to be understood.*

**Castaway: Beyond the Shore** is a 3D survival-adventure game being built from scratch using **Python + OpenGL**.

You wake up stranded in a mysterious, unexplored world. The island contains forests, cliffs, caves, water, wildlife, resources, structures, and places that gradually reveal the story of what happened there.

The goal isn't simply to survive.

**Explore the island, uncover its secrets, build your way toward survival, and eventually find a way home.**

---

## 🎮 Project Status

🚧 **Rendering foundation implemented**

The project has just begun.

### Current Progress

* [x] Project structure created
* [x] Git repository initialized
* [x] Python virtual environment configured
* [x] OpenGL dependencies installed
* [x] First application window created
* [x] OpenGL 4.1 Core rendering (macOS-safe)
* [x] Retina-aware framebuffer handling
* [x] 3D rendering foundation and orbit camera
* [x] Procedural terrain, shadows, water, vegetation, sky, HDR post-process
* [x] Playable terrain-following player and collidable island props
* [ ] Player
* [ ] Survival systems
* [ ] Exploration and story

---

## 🛠️ Technology

* **Python** - Main programming language
* **OpenGL** - 3D rendering
* **GLFW** - Window and input management
* **GLSL** - GPU shaders
* **NumPy** - Mathematical operations
* **Blender** - World and 3D asset creation

The game is intentionally being built without a traditional game engine. The goal is to understand and build the underlying systems ourselves.

---

## 🧠 Development Philosophy

Castaway isn't being built by copying a massive tutorial and hoping it works.

The learning process is:

```text
Learn the concept
      ↓
Understand the math
      ↓
Write it ourselves
      ↓
Put it into Castaway
      ↓
Break it
      ↓
Fix it
      ↓
Understand WHY it works
```

The goal is not just to make a game.

The goal is to understand how the systems behind the game work.

---

## 📁 Project Structure

```text
Castaway/
│
├── assets/
│   ├── models/
│   ├── textures/
│   ├── shaders/
│   ├── sounds/
│   └── fonts/
│
├── src/
│   ├── engine/
│   └── game/
│
├── tests/
├── docs/
│
├── .gitignore
├── README.md
├── requirements.txt
└── LICENSE
```

The project structure will grow as new systems are actually needed rather than creating large numbers of empty files in advance.

## Running on an M1/M2/M3/M4 Mac

The renderer requires a native OpenGL 4.1 Core Profile. Follow the complete setup and architecture guide in [docs/M1_OPENGL_MASTER_GUIDE.md](docs/M1_OPENGL_MASTER_GUIDE.md), then run:

```zsh
source .venv/bin/activate
python -m src.main
```

---

## 🗺️ Development Roadmap

### Phase 1: 🧱 Rendering Foundation

```text
Window
  ↓
OpenGL
  ↓
Triangle
  ↓
Cube
  ↓
3D Camera
  ↓
Meshes
  ↓
Shaders
```

### Phase 2: 🌍 World

The environment will be created with Blender and rendered through the Castaway engine.

```text
Blender
  ↓
Island / Terrain / Structures
  ↓
Export
  ↓
Castaway
  ↓
OpenGL
```

### Phase 3: 🎨 Visuals

```text
Lighting
  ↓
Textures
  ↓
Materials
  ↓
PBR
  ↓
Shadows
  ↓
Water
  ↓
Atmosphere
```

### Phase 4: 🎮 Gameplay

```text
Player
  ↓
Movement
  ↓
Collision
  ↓
Interaction
  ↓
Inventory
  ↓
Crafting
  ↓
Resources
```

### Phase 5: 🐺 Living World

```text
Wildlife
Enemies
AI
Day / Night
Weather
Sound
```

### Phase 6: 📖 The Adventure

```text
Explore
  ↓
Discover locations
  ↓
Find clues
  ↓
Understand the island
  ↓
Unlock new areas
  ↓
Build toward escape
```

---

## 🎨 Rendering Goals

The long-term rendering system will cover:

* 3D coordinate systems
* VBOs
* VAOs
* EBOs
* Cameras
* Matrices and transformations
* GLSL vertex shaders
* Fragment shaders
* Uniforms
* Shader animation
* Normals
* Lighting
* Textures and UVs
* Materials
* PBR
* Transparency
* Shadows
* Water
* Sky and atmosphere
* Fog
* Post-processing
* Optimization

The aim is to gradually build a small rendering engine specifically for Castaway.

---

## 🚀 Long-Term Goal

The end goal isn't:

> "I made a cube in OpenGL."

It's:

> **"I built a 3D game engine, and then used it to make Castaway."**

Starting from a simple window and eventually reaching a complete island survival-adventure.

```text
🔺 Triangle
    ↓
🧊 Cube
    ↓
📷 Camera
    ↓
🌍 World
    ↓
🏝️ Island
    ↓
🧍 Player
    ↓
🎮 Game
    ↓
🚤 Escape
```

---

## 📚 Learning

Castaway is also a learning project.

Every major system should be understood before it becomes part of the game. Documentation, experiments, debugging, and intentionally breaking things are all part of development.

---

## 📝 Development Notes

This project is currently in its earliest stage. Architecture, systems, assets, and gameplay mechanics may change as development progresses.

The README will be updated as Castaway grows.

---

## 🏝️ Castaway: Beyond the Shore

**Explore. Survive. Understand. Escape.**
