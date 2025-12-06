🕒 0:00 – Slide 1: Title（约 40 秒）

讲词：

Hello everyone, my name is Qiyun Ge.
Today I’m presenting our project SILP – Synthetic Indoor Layout Planner.

Our goal is to build a geometry-aware engine that evaluates whether a room layout is feasible and navigable, using pixel-level masks, BFS/A*, and a modular architecture that can be extended by AI later.

🕒 0:40 – Slide 2: Agenda（约 20 秒）

讲词：

Today’s presentation includes six parts:

Introduction

Problem & Motivation

System Architecture

Results and Live Demo

CSP Attempt and Lessons

Future Work

Let’s begin with the introduction.

🕒 1:00 – Slide 3: Introduction（约 50 秒）

讲词：

SILP stands for Synthetic Indoor Layout Planner.

It checks whether a furniture arrangement is valid:

Are objects inside the room?

Are there collisions?

Can a person walk from the door to each furniture item?

To achieve this, we use pixel-based navigation fields, obstacle masks, and BFS/A* search.

This project also serves as a foundation for future AI-based layout generation and synthetic data creation.

🕒 1:50 – Slide 4: Problem（约 45 秒）

讲词：

The main problem is that layout tools do not check feasibility.

A design may look nice visually, but:

The door may be blocked.

The passage may be less than 0.6 meters.

The bed or table may be reachable only in theory, not in reality.

Existing tools focus on drawing and rendering.
They don’t reason at pixel-level obstacles.

SILP fills this gap by generating masks and computing navigable paths.

🕒 2:35 – Slide 5: Motivation – AI / ComfyUI（约 45 秒）

讲词：

Another motivation is the rise of generative AI tools such as ComfyUI.

These tools can create photorealistic room images, but they don’t validate geometry:

A bed might be unreachable.

A layout may be aesthetically good but physically impossible.

SILP acts as a validator before AI generation, ensuring that AI-generated rooms are not only beautiful but also physically realistic and walkable.

🕒 3:20 – Slide 6: System Architecture Overview（约 45 秒）

讲词：

The architecture consists of three parts: Backend, Frontend, and Data Flow.

The backend handles all geometry, coordinate transforms, masks, and path calculations.

The frontend visualizes everything in real time using React and React Three Fiber.

Data is exchanged via REST and WebSocket to support streaming debug images and live navigation paths.

🕒 4:05 – Slide 7: Backend Architecture（约 50 秒）

讲词：

The backend is built with Python + FastAPI.

It includes:

Coordinate systems

Pixel navigation field generation

Clearance masks

BFS and A* implementation

A WebSocket server that streams paths and debug images

The design is modular.
Later, we can replace BFS by other search algorithms or add CSP/RL modules without changing the overall system.

🕒 4:55 – Slide 8: Frontend Architecture（约 50 秒）

讲词：

The frontend uses Next.js and React Three Fiber.

Users can move furniture and immediately see:

New collision masks

Updated BFS/A* results

Whether each furniture item is reachable from the door

The frontend also receives WebSocket messages from the backend and displays the debug path images.

This gives users an intuitive way to understand why a layout fails.

🕒 5:45 – Slide 9: Data Flow（约 40 秒）

讲词：

The data flow is simple:

User provides room size and furniture positions.

Backend constructs pixel masks and runs BFS/A*.

Navigation results and debug images are generated.

Results are streamed to the frontend.

Frontend visualizes the path and feasibility status.

This pipeline is lightweight but powerful, and it supports real-time updates.

🕒 6:25 – Slide 10: Results & Live Demo（约 30 秒）

讲词：

The system is deployed online.

Frontend (Vercel)

Backend (Render)

The demo shows live path recalculation when moving furniture.

Now I will demonstrate a simple example.

➡️ 此处切换到 Demo（2 分钟即可）

🕒 6:55 – 8:55 Demo（约 2 分钟）

讲 Demo 的话术（简短清晰）：

Here is the layout planner interface.

I’ll try moving the furniture to block the door.
As you can see, the planner immediately shows that the path becomes invalid.

Now I move the furniture away…
The path becomes reachable again.

This demonstrates how SILP evaluates walkability in real time.

🕒 8:55 – Slide 11: CSP Attempt & Lessons（约 55 秒）

讲词：

At the beginning, we tried to use Constraint Satisfaction (CSP) to solve the layout problem.

It worked for simple constraints:

Boundary containment

Non-overlap with clearance

But it failed for navigation:

CSP easily gets stuck in local minima

Path feasibility cannot be expressed well as static constraints

The key takeaway:
Navigation is a search problem, not a constraint-only problem.

So CSP is useful, but it must be combined with search algorithms.

🕒 9:50 – Slide 12: Future Work（约 30 秒）

讲词：

In the future, we plan to combine three components:

CSP for hard constraints (Clearance, Safety, Regulations)

Expert System for soft constraints (Aesthetics, Preferences)

Reinforcement Learning to balance both and improve layout quality

This could lead to a fully autonomous layout optimization engine capable of generating designs that are safe, functional, and beautiful.

🕒 10:20 – Final: Thank You（约 10 秒）

讲词：

Thank you for listening.
I’m happy to answer any questions.