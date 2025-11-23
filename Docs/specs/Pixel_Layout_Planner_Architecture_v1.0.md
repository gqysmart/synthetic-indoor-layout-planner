# Pixel-Driven Indoor Layout Planner – Algorithm & Visualization Architecture
**Version 1.0**  
**Author: Grant**

---

# 1. 概述 (Overview)

本系统基于三层架构实现室内家具布局规划，并提供完整的动态搬运动画展示流程：

1. **布局方式双模式**
   - **手动布置 (Manual Layout)**：前端拖拽决定家具摆放。
   - **自动布局 (Algorithmic Layout)**：基于几何约束（CSP）、距离变换（EDT）、路径搜索自动生成布局。

2. **动态搬运模拟 (Furniture Delivery Simulation)**
   - 家具逐件从门口“进入”并移动到目标位置。
   - Pixel 层执行 BFS、EDT、占用栅格等算法。
   - 前端 three.js 用 WebSocket 动态展示 3D 家具动画。

系统通过 **Pixel 层作为计算核心**，实现可解释、可调试、可展示的室内布局规划与路径模拟。

---

# 2. 系统整体架构 (System Architecture)

```
┌──────────────────────────────────────────────┐
│      Layout Planning (手动 / 自动布局)        │
│  - Manual: 用户拖动                           │
│  - Auto: CSP + BFS/EDT                        │
└──────────────────────────────────────────────┘
                      ↓ LayoutPlan
┌──────────────────────────────────────────────┐
│       Layout Representation (布局方案)         │
│  - Room, Furniture, Shape, Transform          │
│  - LayoutPlan: 统一描述布局结果               │
└──────────────────────────────────────────────┘
                      ↓ motion plans
┌──────────────────────────────────────────────┐
│   Pixel Layer (算法核心 / Occupancy Grid)     │
│  - World → Pixel 离散化                        │
│  - BFS / EDT / Morphology                      │
│  - Path Planning（家具路径）                   │
│  - Debug Textures (PNG)                        │
└──────────────────────────────────────────────┘
                   ↓ WebSocket JSON / PNG
┌──────────────────────────────────────────────┐
│      Frontend Visualization (three.js)        │
│  - 3D 家具动画                                │
│  - Pixel 层 debug 图像叠加                     │
└──────────────────────────────────────────────┘
```

Pixel 层负责“逻辑”，Three.js 层负责“展示”。

---

# 3. 三层坐标系统 (Coordinate Systems)

系统内部采用三层坐标体系：

## 3.1 Local Coordinate（局部坐标）
每个 Shape（矩形、圆弧）在自身局部坐标中定义。

例如：
- 矩形家具顶点在局部坐标以 (0,0) 为中心。

## 3.2 World Coordinate（世界坐标，单位：米）
- +x 向右  
- +y 向上  
- 家具通过 `Transform` 从局部坐标放置到世界坐标。

## 3.3 Pixel Coordinate（像素坐标）
用于：
- EDT、膨胀/腐蚀
- BFS 路径搜索
- 栅格占用图构建
- Debug 图片生成

也是算法的真正工作空间。

该层通过 `PixelCoordinateSystem` 完成 world→pixel 变换。

---

# 4. 布局方案模型 (LayoutPlan Model)

所有布局结果（无论手动或自动）统一为以下结构：

```python
@dataclass
class FurniturePlacement:
    furniture: Furniture
    transform: Transform  # 家具最终位置（世界坐标）

@dataclass
class LayoutPlan:
    room: Room
    placements: List[FurniturePlacement]
    mode: Literal["manual", "auto"]
```

优势：
- 前后端通用
- 布局、路径、动画数据都基于此

---

# 5. 布局方式设计 (Manual + Auto)

## 5.1 手动模式 (Manual Layout)

流程：
1. 前端拖拽更新家具 Transform  
2. 后端验证：
   - 边界约束（inside room）
   - 膨胀后不重叠（clearance overlap）
   - 门到家具是否可达（BFS/EDT）
3. 若通过 → 返回 `LayoutPlan(mode="manual")`

---

## 5.2 自动模式 (Algorithmic Layout)

使用 Stage 1 强几何 CSP：
- 离散化成像素栅格
- OverlapCost(L) = 越界面积 + 膨胀后重叠面积
- 用 hill-climbing / 随机扰动压缩 overlap cost
- 通道宽度用 BFS/EDT 检查

输出一组 Transform → `LayoutPlan(mode="auto")`

---

# 6. 动态搬运动画系统 (Furniture Delivery Simulation)

家具依次从门口被“搬运”到布局方案的目标位置。

### MotionPlan 数据结构

```python
@dataclass
class FurnitureMotionPlan:
    furniture: Furniture
    path: List[Transform]  # 路径上的每一帧姿态
```

系统对每件家具生成一条路径。

---

# 7. 路径规划算法 (Path Planning)

两阶段：

---

## 7.1 MVP：线性插值（直线移动）

- 起点：门口 Transform  
- 终点：目标 Transform  
- 用 linear interpolation (lerp) 创建路径：

```python
xs = np.linspace(start.x, end.x, steps)
ys = np.linspace(start.y, end.y, steps)
rs = np.linspace(start.r, end.r, steps)
```

适合演示效果。

---

## 7.2 完整路径规划：基于 Pixel 层 BFS / A\*

流程：
1. 世界几何投影成 occupancy grid  
2. 膨胀（distance transform）扩大障碍  
3. BFS / A* 搜索“家具中心点路径”  
4. 将路径点转换成 Transform（含角度 r）

一次只移动一件家具，其余家具视为静态障碍。

---

# 8. Pixel 层设计 (核心算法层)

Pixel 层负责：

- 世界几何 rasterization
- occupancy grid 生成
- distance transform
- 膨胀 / 腐蚀
- 去噪 / skeletonization（可选）
- 路径搜索（BFS/A*）
- Debug 图像渲染（PNG）

特点：

> Pixel 层是算法的“物理引擎”，不依赖前端渲染。

---

# 9. Pixel → Three.js 的 WebSocket 联动

前端通过 WebSocket 以实时动画展示算法结果。

---

## 9.1 数据类型 A：结构化语义数据（three.js 主用）

示例：

```json
{
  "type": "layoutPlan",
  "data": {
    "room": { "polygon": [[-2,-1],[2,-1],[2,1],[-2,1]] },
    "furnitures": [
      { "id": "bed1", "final": {"x":1.2,"y":-0.8,"r":90} }
    ]
  }
}
```

路径数据：

```json
{
  "type": "motionPlan",
  "data": {
    "furnitureId": "bed1",
    "path": [
      {"x":0.3,"y":-1.4,"r":0},
      {"x":0.7,"y":-1.2,"r":30},
      {"x":1.0,"y":-1.0,"r":60},
      {"x":1.2,"y":-0.8,"r":90}
    ]
  }
}
```

three.js 用这些驱动 Mesh：

```js
mesh.position.set(x, 0, y);
mesh.rotation.y = THREE.MathUtils.degToRad(r);
```

---

## 9.2 数据类型 B：Pixel Debug 图像

例如：
- EDT 灰度图  
- occupancy grid  
- corridor mask  
- path mask  

后端将其编码成 base64 PNG：

```json
{
  "type": "debugImage",
  "format": "png",
  "data": "<base64>"
}
```

three.js 中贴图展示：

```js
const tex = new THREE.TextureLoader().load(base64Url);
```

---

# 10. 动画渲染 (Frame Rendering)

动画循环：

```
for furniture in placements:
    motion = motion_plan(furniture)
    for tf in motion.path:
        render_frame(tf)
```

关键步骤：
- 每帧将局部顶点用 Transform 转世界  
- 再 world → pixel → OpenCV 或 JSON（WebSocket）
- 前端更新 Mesh 位置

---

# 11. End-to-End 数据流 (Data Flow)

```
Shape (local)
   → Transform.local_to_world()
World vertices
   → PixelCoordinateSystem.world_to_pixel()
Pixel grid
   → Path Planning
Motion path (x,y,r)
   → WebSocket JSON
three.js 动画渲染
```

Pixel 层负责科学计算；three.js 负责效果展示。

---

# 12. 系统优势 (Advantages)

- **算法与渲染彻底解耦**
- **Pixel 层可本地 `cv.imshow` 调试**
- three.js 提供：
  - 更好视觉效果
  - 3D 动画
  - 灯光/阴影
  - 即时交互（浏览器可用）
- 整体可用于：
  - 课程展示  
  - Portfolio 项目  
  - 产品原型  
  - 演示优化算法可达性  

---

# 13. 项目实现路线图 (Roadmap)

## 阶段 1：后端

- [ ] 完成 LayoutPlan
- [ ] Pixel 层 occupancy grid
- [ ] 通道 / 不重叠检查
- [ ] 线性路径动画（MVP）

## 阶段 2：前端

- [ ] three.js 3D 场景
- [ ] Mesh 动画播放
- [ ] 接收布局与路径数据
- [ ] debug 图像叠加

## 阶段 3：完整系统

- [ ] BFS/A* 完整路径规划
- [ ] 家具顺序规划优化
- [ ] 平滑曲线（spline）路径
- [ ] 更丰富 UI

---

# 完毕

如需生成：
- PDF 版  
- PPT（Marp）版  
- GitHub README 自动版  
- three.js starter template  

请告诉我。