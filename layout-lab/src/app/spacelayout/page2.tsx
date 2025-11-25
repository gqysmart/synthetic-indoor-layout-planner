// app/layout/page.tsx
"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";

type Algorithm = "bfs" | "csp" | "hybrid";

type RoomOption = {
  id: string;
  name: string;
  size: string;
};

type FurnitureOption = {
  id: string;
  name: string;
  size: string;
};

const ROOMS: RoomOption[] = [
  {
    id: "room-a",
    name: "Room A – 3m × 4m",
    size: "3.0m × 4.0m",
  },
  {
    id: "room-b",
    name: "Room B – L-shape",
    size: "4.5m × 5.0m (L)",
  },
];

const FURNITURES: FurnitureOption[] = [
  {
    id: "sofa",
    name: "Sofa",
    size: "2.0m × 0.9m",
  },
  {
    id: "bed",
    name: "Bed",
    size: "1.5m × 2.0m",
  },
  {
    id: "desk",
    name: "Desk",
    size: "1.2m × 0.6m",
  },
];

// 用来给房间一个简单的尺寸配置（米）
const ROOM_CONFIG: Record<
  string,
  { width: number; depth: number }
> = {
  "room-a": { width: 3.0, depth: 4.0 },
  "room-b": { width: 4.5, depth: 5.0 },
};

// 家具简单尺寸配置（米）
const FURNITURE_CONFIG: Record<
  string,
  { width: number; depth: number; height: number }
> = {
  sofa: { width: 2.0, depth: 0.9, height: 0.8 },
  bed: { width: 2.0, depth: 1.5, height: 0.6 },
  desk: { width: 1.2, depth: 0.6, height: 0.75 },
};

/* ---------- Three.js 场景组件 ---------- */

type LayoutSceneProps = {
  algorithm: Algorithm;
  roomId: string;
  furnitureIds: string[];
};

function LayoutScene({ algorithm, roomId, furnitureIds }: LayoutSceneProps) {
  const roomConfig = ROOM_CONFIG[roomId] ?? { width: 3, depth: 4 };

  // 简单把家具排成一条线，之后可以换成你的布局结果
  const furnitureInstances = useMemo(() => {
    return furnitureIds.map((id, index) => {
      const cfg = FURNITURE_CONFIG[id] ?? {
        width: 1,
        depth: 1,
        height: 0.5,
      };
      const spacing = 0.3;
      const x = -roomConfig.width / 2 + cfg.width / 2 + index * (cfg.width + spacing);
      const z = 0; // 先都放在房间中轴线上
      return {
        id,
        ...cfg,
        position: [x, cfg.height / 2, z] as [number, number, number],
      };
    });
  }, [furnitureIds, roomConfig]);

  // 不同算法给一点颜色反馈（纯视觉）
  const roomColor =
    algorithm === "csp"
      ? "#6b7280" // slate-500
      : algorithm === "bfs"
      ? "#0f766e" // teal-700
      : "#7c3aed"; // violet-600

  return (
    <>
      {/* 环境光 + 平行光 */}
      <ambientLight intensity={0.6} />
      <directionalLight
        position={[5, 10, 4]}
        intensity={1.2}
        castShadow
      />

      {/* 地面 / 房间平面 */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        {/* 放大一点给一点留白 */}
        <planeGeometry
          args={[roomConfig.width + 1, roomConfig.depth + 1]}
        />
        <meshStandardMaterial color="#020617" />
      </mesh>

      {/* 房间边界（细一点的 plane ） */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        receiveShadow
      >
        <planeGeometry
          args={[roomConfig.width, roomConfig.depth]}
        />
        <meshStandardMaterial
          color={roomColor}
          opacity={0.35}
          transparent
        />
      </mesh>

      {/* 网格作为视觉辅助 */}
      <Grid
        position={[0, 0.02, 0]}
        args={[10, 10]}
        cellSize={0.5}
        cellThickness={0.4}
        infiniteGrid
        fadeDistance={25}
        fadeStrength={1}
      />

      {/* 家具实例（简单 Box） */}
      {furnitureInstances.map((f) => (
        <mesh
          key={f.id + JSON.stringify(f.position)}
          position={f.position}
          castShadow
        >
          <boxGeometry
            args={[f.width, f.height, f.depth]}
          />
          <meshStandardMaterial color="#e5e7eb" />
        </mesh>
      ))}

      {/* 轨道相机控制 */}
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        target={[0, 0.4, 0]}
        maxPolarAngle={Math.PI / 2.1}
      />
    </>
  );
}

/* ---------- 页面本体 ---------- */

export default function LayoutPage() {
  const [algorithm, setAlgorithm] = useState<Algorithm>("csp");
  const [selectedRoomId, setSelectedRoomId] = useState<string>("room-a");
  const [selectedFurnitureIds, setSelectedFurnitureIds] = useState<string[]>([]);

  const selectedRoom = ROOMS.find((r) => r.id === selectedRoomId);

  const toggleFurniture = (id: string) => {
    setSelectedFurnitureIds((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const handleRun = () => {
    // TODO: 将来这里接你的 Python 后端 / 算法
    console.log("Run layout algorithm with:", {
      algorithm,
      selectedRoomId,
      selectedFurnitureIds,
    });
    alert("Layout algorithm started (stub).");
  };

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-baseline gap-2">
            <h1 className="text-xl font-semibold tracking-tight">
              Layout Lab
            </h1>
            <span className="text-xs text-slate-500">
              / Layout Playground
            </span>
          </div>
          <nav className="flex gap-4 text-sm">
            <Link
              href="/"
              className="text-slate-500 hover:text-slate-900"
            >
              Home
            </Link>
            <span className="font-medium text-slate-900">Layout</span>
          </nav>
        </div>
      </header>

      {/* 主体区域 */}
      <section className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-6 lg:flex-row">
        {/* 左侧控制面板 */}
        <aside className="flex w-full flex-col gap-4 lg:w-80">
          {/* 1. 基本介绍 */}
          <section className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Overview
            </h2>
            <p className="mt-2 text-sm text-slate-700">
              Configure the room, choose a layout algorithm, add furniture,
              then run the solver to visualize the placement in 3D.
            </p>
          </section>

          {/* 2. 算法选择 */}
          <section className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Algorithm
            </h2>

            <div className="mt-3 space-y-2">
              <label className="flex cursor-pointer items-center justify-between rounded-xl border px-3 py-2 text-sm hover:bg-slate-50">
                <div>
                  <span className="font-medium">CSP Heuristic</span>
                  <p className="text-xs text-slate-500">
                    Minimize overlap + boundary violations with heuristic
                    search.
                  </p>
                </div>
                <input
                  type="radio"
                  name="algorithm"
                  className="h-4 w-4"
                  checked={algorithm === "csp"}
                  onChange={() => setAlgorithm("csp")}
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between rounded-xl border px-3 py-2 text-sm hover:bg-slate-50">
                <div>
                  <span className="font-medium">BFS Reachability</span>
                  <p className="text-xs text-slate-500">
                    Check door-to-furniture paths using BFS on the grid.
                  </p>
                </div>
                <input
                  type="radio"
                  name="algorithm"
                  className="h-4 w-4"
                  checked={algorithm === "bfs"}
                  onChange={() => setAlgorithm("bfs")}
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between rounded-xl border px-3 py-2 text-sm hover:bg-slate-50">
                <div>
                  <span className="font-medium">Hybrid</span>
                  <p className="text-xs text-slate-500">
                    Combine CSP for collisions and BFS for corridors.
                  </p>
                </div>
                <input
                  type="radio"
                  name="algorithm"
                  className="h-4 w-4"
                  checked={algorithm === "hybrid"}
                  onChange={() => setAlgorithm("hybrid")}
                />
              </label>
            </div>
          </section>

          {/* 3. 房间选择 */}
          <section className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Room
            </h2>

            <div className="mt-3 space-y-3">
              {ROOMS.map((room) => (
                <button
                  key={room.id}
                  type="button"
                  onClick={() => setSelectedRoomId(room.id)}
                  className={`flex w-full items-center gap-3 rounded-xl border p-2 text-left text-sm hover:bg-slate-50 ${
                    selectedRoomId === room.id
                      ? "border-slate-900 bg-slate-900/5"
                      : "border-slate-200"
                  }`}
                >
                  <div className="h-12 w-16 flex-shrink-0 overflow-hidden rounded-lg bg-slate-100">
                    <div className="flex h-full w-full items-center justify-center text-[10px] text-slate-400">
                      {room.name.split("–")[0]}
                    </div>
                  </div>
                  <div>
                    <p className="font-medium">{room.name}</p>
                    <p className="text-xs text-slate-500">
                      {room.size}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* 4. 家具添加 */}
          <section className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Furniture
            </h2>

            <div className="mt-3 max-h-44 space-y-2 overflow-y-auto pr-1">
              {FURNITURES.map((f) => {
                const selected = selectedFurnitureIds.includes(f.id);
                return (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => toggleFurniture(f.id)}
                    className={`flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-sm hover:bg-slate-50 ${
                      selected
                        ? "border-emerald-500 bg-emerald-50"
                        : "border-slate-200"
                    }`}
                  >
                    <div>
                      <p className="font-medium">{f.name}</p>
                      <p className="text-xs text-slate-500">
                        {f.size}
                      </p>
                    </div>
                    <span className="text-xs font-medium text-slate-400">
                      {selected ? "Added" : "Add"}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          {/* 5. 执行按钮 */}
          <section className="mt-auto rounded-2xl border bg-white p-4 shadow-sm">
            <button
              type="button"
              onClick={handleRun}
              className="inline-flex w-full items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 active:bg-slate-950"
            >
              Run Layout Algorithm
            </button>
            <p className="mt-2 text-xs text-slate-500">
              The current selection will be sent to the solver and the result
              will be rendered in the 3D viewport.
            </p>
          </section>
        </aside>

        {/* 右侧 Three.js 显示区域 */}
        <section className="flex-1">
          <div className="flex h-[520px] flex-col rounded-2xl border bg-white shadow-sm">
            {/* 顶部状态栏 */}
            <div className="flex items-center justify-between border-b px-4 py-2">
              <div className="flex flex-col">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  3D Viewport
                </span>
                <span className="text-xs text-slate-500">
                  Room: {selectedRoom?.name ?? "None"} · Algorithm:{" "}
                  {algorithm.toUpperCase()} · Furniture:{" "}
                  {selectedFurnitureIds.length}
                </span>
              </div>
              <div className="flex gap-2 text-xs text-slate-500">
                <span className="rounded-full border px-3 py-1">
                  R3F / Orbit
                </span>
              </div>
            </div>

            {/* Three.js Canvas */}
            <div className="flex-1">
              <Canvas
                shadows
                camera={{ position: [5, 5, 6], fov: 45 }}
              >
                <LayoutScene
                  algorithm={algorithm}
                  roomId={selectedRoomId}
                  furnitureIds={selectedFurnitureIds}
                />
              </Canvas>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
