# SILP 项目架构说明（内部文档）

## 1. 项目总体诉求

SILP 项目包含三个核心目标：

1.  **布局编辑由 Next.js 完成（Client 1）**
    -   房间尺寸、家具选择、家具位置与角度均由前端管理\
    -   用户交互（Room Layout Editor）发生在浏览器端\
    -   布局数据由前端上传给后端进行算法处理
2.  **FastAPI 提供算法层能力**
    -   寻路（A\* / BFS 等）\
    -   可达性分析\
    -   家具碰撞检测、布局合法性检验\
    -   导航场、障碍物 mask 等 debug 图片生成\
    -   返回路径 / 校验结果 / debug 资源 URL
3.  **家具规格（specs）由数据库保存，但管理责任在 FastAPI**
    -   specs 存在共享数据库中\
    -   **FastAPI 是唯一的 CRUD 管理者（Single Source of Truth）**\
    -   Next.js（包括前台和后台）均通过 FastAPI 的 API 获取或更新 specs\
    -   Next.js 不直接连接数据库

## 2. 系统角色职责划分

### 2.1 Next.js（Client 1：主前端）

-   提供 Room Layout 编辑器：
    -   房间选择\
    -   家具库列表\
    -   家具拖拽摆放\
    -   设置位置 / 旋转\
-   从后端拉取 specs\
-   将布局数据发送给 FastAPI 进行算法处理\
-   展示路径、布局校验结果\
-   不直接访问数据库

### 2.2 Next.js（Client 2：管理后台 Admin）

-   展示 debug 图片\
-   展示算法分数、路径结果\
-   管理 specs 的 UI（新增/修改/删除）\
-   所有更新通过 FastAPI 完成

### 2.3 FastAPI Backend（算法核心 + spec 管理者）

-   访问与管理共享数据库（specs）\
-   提供算法服务\
-   提供 debug 图片服务\
-   提供 specs CRUD API\
-   是 specs 的 Single Source of Truth

## 3. 数据流设计

### 3.1 前端 → 后端（算法请求）

``` json
{
  "room": { "width": 3.6, "height": 3.3 },
  "furniture": [
    { "id": "bed1", "spec_id": "bed_180x200", "x": 1.8, "y": 1.1, "theta": 90 },
    { "id": "wardrobe1", "spec_id": "wardrobe_180x60", "x": 2.9, "y": 0.9, "theta": 0 }
  ],
  "agent": {
    "start": { "x": 0.5, "y": 0.5 },
    "goal": { "x": 3.0, "y": 2.5 }
  },
  "options": {
    "need_debug_images": true
  }
}
```

FastAPI 返回：

``` json
{
  "run_id": "20251127-093001-abc",
  "success": true,
  "path": [...],
  "metrics": { "reachable": true, "length": 2.5 },
  "debug_images": {
    "overview": "/api/debug/20251127-093001-abc/overview.png",
    "mask": "/api/debug/20251127-093001-abc/mask.png"
  }
}
```

## 4. 家具 Specs 数据管理模式

### 原则：

**Specs 放在共享数据库中，但数据库只允许 FastAPI 访问并管理。**

Next.js 前台和后台通过 API 与 specs 交互：

    GET    /api/specs
    POST   /api/specs
    PUT    /api/specs/{id}
    DELETE /api/specs/{id}

优势：

-   业务逻辑集中\
-   所有前端可复用同一 API\
-   减少 Next.js 直接操作数据库带来的耦合与安全问题

## 5. 架构总结

> **Next.js 负责布局编辑并上传布局；FastAPI 负责所有算法和 debug
> 输出；家具 specs 存在数据库里，但只有 FastAPI 管理，Next.js 通过 API
> 使用 specs。**
