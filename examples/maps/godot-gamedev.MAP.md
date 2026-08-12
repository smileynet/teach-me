---
domain: godot-gamedev
description: "Build playable 2D and 3D games with the Godot engine — from scene architecture through polish to publishing"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - shader-programming
  - multiplayer-networking
  - procedural-generation
  - game-ai-and-behavior
  - publishing-and-marketing
---

# Game Development with Godot

## Orientation

Godot is a free, open-source game engine whose node/scene architecture makes it unusually learnable — every game object is a composable tree of small, focused nodes. You'll go from understanding how Godot thinks about game objects to shipping a complete game, covering scripting, physics, UI, and polish along the way.

## Topics

### nodes-and-scenes
- **title:** Nodes, Scenes & the Scene Tree
- **why:** Everything in Godot is a node in a tree — understanding this architecture is the foundation for every project
- **scope:** substantial
- **prereqs:** []
- **leads_to:** [game-ai-and-behavior]
- **status:** not-started

### gdscript-fundamentals
- **title:** GDScript Fundamentals
- **why:** GDScript is how you give nodes behavior — variables, functions, signals, and lifecycle callbacks make your game respond to the player
- **scope:** substantial
- **prereqs:** [nodes-and-scenes]
- **status:** not-started

### 2d-game-mechanics
- **title:** 2D Game Mechanics
- **why:** 2D is where most Godot learners build their first complete game — movement, collision, tilemaps, and camera work
- **scope:** deep
- **prereqs:** [gdscript-fundamentals]
- **leads_to:** [procedural-generation]
- **status:** not-started

### physics-and-collision
- **title:** Physics & Collision Systems
- **why:** Rigid bodies, areas, raycasts, and collision layers are how your game world enforces physical rules
- **scope:** substantial
- **prereqs:** [nodes-and-scenes, gdscript-fundamentals]
- **status:** not-started

### ui-and-control-nodes
- **title:** UI, Menus & HUD
- **why:** Every game needs at least a title screen and a score counter — Godot's Control nodes are a full UI toolkit built into the engine
- **scope:** substantial
- **prereqs:** [gdscript-fundamentals]
- **status:** not-started

### animation-and-audio
- **title:** Animation & Audio
- **why:** AnimationPlayer, tweens, and the audio bus system turn a functional prototype into something that feels alive
- **scope:** substantial
- **prereqs:** [nodes-and-scenes, gdscript-fundamentals]
- **leads_to:** [shader-programming]
- **status:** not-started

### 3d-fundamentals
- **title:** 3D Fundamentals
- **why:** Godot's 3D pipeline shares the same node/scene model — once you know 2D, 3D is a spatial upgrade, not a rewrite
- **scope:** deep
- **prereqs:** [2d-game-mechanics, physics-and-collision]
- **leads_to:** [shader-programming]
- **status:** not-started

### exporting-and-publishing
- **title:** Exporting & Publishing
- **why:** A game isn't done until someone can play it — export templates, platform quirks, and distribution channels
- **scope:** lightweight
- **prereqs:** [2d-game-mechanics]
- **leads_to:** [publishing-and-marketing]
- **status:** not-started
