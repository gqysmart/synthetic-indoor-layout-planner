'use client'

import { Canvas } from "@react-three/fiber"
import Link from "next/link"
import { Grid, OrbitControls } from "@react-three/drei"
import { FurnitureModel3D } from "@/components/3Dmodels/furniture3D"
import { Character } from "@/components/3Dmodels/character"
import { useMemo, useState, memo, useEffect, useCallback } from "react"
import { usePlannerSocket } from "@/hooks/usePlannerSocket"

import { LayoutDTO, WsIncomingMessage } from "@/lib/types/websocketMessage"
import { LayoutPreview } from "@/components/ui/layoutPreview"

export default function RoomLayoutPage() {
    const [wsUrl, setWsUrl] = useState<string | null>(null)
    const [path, setPath] = useState<[number, number][] | null>([])
    const [data_layout, set_data_layout] = useState<LayoutDTO[] | null>([])
    const [selected, set_selected] = useState<number | null>(null)

    const algorithms = ["csp", "A*"]
    const [algorithm_selected, set_algorithm_selected] = useState<number>(0)

    const context_selected_layout: RoomLayoutContext = {
        layout_selected: selected,
        layouts: data_layout,
        algorithm: algorithms[algorithm_selected],
        path: path,
    }

    const url_for_jobId = "/api/plan/jobs"

    const handlePlannerMessage = useCallback((msg: WsIncomingMessage) => {
        if (msg.type === "status") {
            console.log("Websocket Status update:", msg.payload?.message)
        } else if (msg.type === "error") {
            console.error("Error from websocket server:", msg.payload?.message)
        } else if (msg.type === "path_response") {
            if (msg.payload?.command === "start_path_finding") {
                setPath(msg.payload.path)
            }
            console.log("Response from websocket server:", msg.payload)
        } else if (msg.type === "layout_response") {
            if (msg.payload?.command === "get_example_layout") {
                const layout = msg.payload.layout
                console.log("Received example layout:", layout)
                set_data_layout(layout)
                if (layout.length > 0) {
                    set_selected(0)
                }
            }
        }
    }, [])

    const { status, startSocket, sendCommand, stopSocket } =
        usePlannerSocket(handlePlannerMessage)

    // 拿到 websocket server url
    useEffect(() => {
        async function fetchWS() {
            const response = await fetch(url_for_jobId, { method: "POST" })
            const data = await response.json()
            if (!data.server_url) {
                console.error("Invalid response:", data)
            } else {
                setWsUrl(data.server_url)
            }
        }
        fetchWS()
    }, [])

    // 根据 wsUrl 建立/关闭连接
    useEffect(() => {
        if (!wsUrl) return
        console.log("Starting websocket with url:", wsUrl)
        startSocket(wsUrl)
        return () => {
            stopSocket()
        }
    }, [wsUrl, startSocket, stopSocket])

    return (
        <main className="h-screen bg-slate-100 text-slate-900 flex flex-col">
            {/* Header */}
            <header className="h-14 flex items-center justify-between px-6 border-b border-slate-200 bg-white">
                <div className="flex items-center gap-3">
                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600 text-sm font-semibold">
                        LL
                    </span>
                    <div>
                        <h1 className="text-sm font-semibold tracking-wide">
                            SILP Layout Lab
                        </h1>
                        <p className="text-xs text-slate-500">
                            Synthetic Indoor Layout Planner
                        </p>
                    </div>
                </div>

                <nav className="text-xs text-slate-500 flex items-center gap-4">
                    <Link href="/" className="hover:text-slate-800 transition">
                        Home
                    </Link>
                </nav>
            </header>

            {/* Main Content: 三列布局 */}
            <section className="flex-1 flex min-h-0 gap-4 px-4 py-4">
                {/* 左列：Layout Library */}
                <aside className="w-72 flex-shrink-0 bg-white rounded-lg border border-slate-200 shadow-sm p-4 overflow-y-auto">
                    <h2 className="text-xs font-semibold tracking-wide text-slate-700 mb-3 uppercase">
                        Layout Library
                    </h2>

                    <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3 text-xs space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-700">Layouts</span>
                            <span className="text-[11px] text-slate-500">
                                {data_layout?.length ?? 0} loaded
                            </span>
                        </div>

                        <button
                            className="w-full rounded-md bg-blue-500 text-white text-[11px] font-medium py-1.5 hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={() =>
                                sendCommand({
                                    type: "command",
                                    payload: { command: "get_example_layout" },
                                })
                            }
                            disabled={!wsUrl}
                        >
                            Refresh layouts
                        </button>

                        <div className="space-y-2">
                            <label className="block text-[11px] text-slate-500">
                                Choose layout
                            </label>
                            <select
                                value={selected !== null ? String(selected) : ""}
                                onChange={(e) =>
                                    set_selected(
                                        e.target.value === "" ? null : Number(e.target.value)
                                    )
                                }
                                className="w-full border border-slate-300 bg-white text-xs rounded-md px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="">Select a layout…</option>
                                {data_layout?.map((layout, index) => (
                                    <option key={layout.name} value={index}>
                                        {layout.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Layout 简要信息，模仿截图里的 Room Info / Furniture count */}
                        {selected !== null && data_layout && data_layout[selected] && (
                            <div className="mt-1 space-y-1 text-[11px] text-slate-600">
                                <p>
                                    <span className="font-semibold">Room info:</span>{" "}
                                    {data_layout[selected].room.width} ×{" "}
                                    {data_layout[selected].room.height}
                                </p>
                                <p>
                                    <span className="font-semibold">Furniture count:</span>{" "}
                                    {data_layout[selected].furnitures.length}
                                </p>
                            </div>
                        )}
                    </div>

                    {/* 2D 预览小卡片 */}
                    <div className="mt-4 rounded-lg border border-slate-200 bg-white overflow-hidden">
                        <LayoutPreview
                            layout={
                                selected !== null && data_layout ? data_layout[selected] : null
                            }
                        />
                    </div>
                </aside>

                {/* 中间列：3D Viewport */}
                <section className="flex-1 flex flex-col min-h-0 bg-white rounded-lg border border-slate-200 shadow-sm">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-slate-50">
                        <h2 className="text-xs font-semibold text-slate-700 tracking-wide uppercase">
                            3D Viewport
                        </h2>
                        <div className="text-[11px] text-slate-500">
                            Algo:{" "}
                            <span className="text-slate-800 font-medium">
                                {algorithms[algorithm_selected]}
                            </span>
                        </div>
                    </div>

                    <Canvas
                        shadows
                        dpr={[1, 2]}
                        camera={{ position: [5, 5, 5], fov: 50 }}
                        className="flex-1 bg-slate-100 rounded-b-lg"
                    >
                        <LayoutScene context={context_selected_layout} />
                    </Canvas>

                    <footer className="mt-auto py-3 text-center text-[11px] text-slate-400 border-t border-slate-200 bg-white rounded-b-lg">
                        © 2025 ACE AI · Layout Lab
                    </footer>
                </section>

                {/* 右列：Setup + Path finding */}
                <aside className="w-72 flex-shrink-0 bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-4">
                    <h2 className="text-xs font-semibold tracking-wide text-slate-700 mb-1 uppercase">
                        Setup
                    </h2>

                    {/* WebSocket 状态 */}
                    <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3 text-xs space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-700">WebSocket</span>
                            <StatusBadge status={status} />
                        </div>
                        <p className="text-[11px] text-slate-500 break-all leading-relaxed">
                            {wsUrl ?? "Waiting for server URL…"}
                        </p>
                    </div>

                    {/* Path finding 控制 */}
                    <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3 text-xs space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-700">Path finding</span>
                            <span className="text-[11px] text-slate-500">Algorithm</span>
                        </div>

                        <select
                            className="w-full border border-slate-300 bg-white text-xs rounded-md px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            value={algorithm_selected}
                            onChange={(e) => set_algorithm_selected(Number(e.target.value))}
                        >
                            {algorithms.map((algo, idx) => (
                                <option key={algo} value={idx}>
                                    {algo}
                                </option>
                            ))}
                        </select>

                        <button
                            className="w-full mt-1 rounded-md bg-emerald-500 text-emerald-950 text-[11px] font-medium py-1.5 hover:bg-emerald-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={() => {
                                if (wsUrl && selected !== null) {
                                    console.log(
                                        "Sending path finding command with selected layout index:",
                                        selected
                                    )
                                    sendCommand({
                                        type: "command",
                                        payload: {
                                            command: "start_path_finding",
                                            parameters: { selected },
                                        },
                                    })
                                }
                            }}
                            disabled={!wsUrl || selected === null}
                        >
                            Find path for current layout
                        </button>

                        {path && path.length > 0 && (
                            <p className="text-[11px] text-emerald-600 mt-1">
                                Path loaded: {path.length} points
                            </p>
                        )}
                    </div>
                </aside>
            </section>
        </main>
    )
}

type RoomLayoutContext = {
    path: [number, number][] | null
    layout_selected: number | null
    layouts: LayoutDTO[] | null
    algorithm: string | null
}

const LayoutScene = memo(function LayoutScene({ context }: { context: RoomLayoutContext }) {
    const { path, algorithm, layouts, layout_selected } = context
    console.log("Rendering LayoutScene with context:", context)

    return (
        <>
            {/* 浅色背景 */}
            <color attach="background" args={["#f9fafb"]} />

            <ambientLight intensity={0.8} />
            <hemisphereLight groundColor="#dddddd" intensity={0.6} />
            <directionalLight
                position={[5, 10, 5]}
                intensity={1.4}
                shadow-mapSize-width={2048}
                shadow-mapSize-height={2048}
                castShadow
            />

            <Character path={path} />

            <OrbitControls
                enablePan
                enableZoom
                enableRotate
                target={[0, 0.4, 0]}
                maxPolarAngle={Math.PI / 2.1}
            />

            <fog attach="fog" args={["#e5e7eb", 30, 160]} />

            <Grid
                args={[10, 10]}
                position={[0, -0.001, 0]}
                cellSize={0.5}
                cellThickness={0.5}
                sectionSize={2}
                sectionThickness={1}
                fadeDistance={40}
                fadeStrength={1}
            />

            {layouts && layout_selected !== null ? (
                <RoomAndFurnitures layouts={layouts} selected={layout_selected} path={path} />
            ) : (
                <mesh
                    receiveShadow
                    rotation={[-Math.PI / 2, 0, 0]}
                    position={[0, 0, 0]}
                >
                    <planeGeometry args={[3.6, 3.3]} />
                    <meshStandardMaterial color="#e5e7eb" />
                </mesh>
            )}
        </>
    )
})

const RoomAndFurnitures = memo(function RoomAndFurnitures({
    layouts,
    selected,
    path,
}: {
    layouts: LayoutDTO[]
    selected: number
    path: [number, number][] | null
}) {
    console.log("Rendering RoomAndFurnitures with selected layout:", layouts[selected])
    const layout = layouts[selected]
    const furnitures = layout.furnitures

    return (
        <>
            <Room width={layout.room.width} height={layout.room.height} />
            {furnitures.map((furniture, idx) => (
                <FurnitureModel3D
                    key={idx}
                    props={{
                        name: furniture.type,
                        position: [furniture.position[0], furniture.position[1]],
                        rotation: (furniture.rotation * Math.PI) / 180,
                        width: furniture.width,
                        height: furniture.height,
                    }}
                />
            ))}
        </>
    )
})

function Room({ width, height }: { width: number; height: number }) {
    return (
        <mesh
            receiveShadow
            rotation={[-Math.PI / 2, 0, 0]}
            position={[0, 0, 0]}
        >
            <planeGeometry args={[width, height]} />
            <meshStandardMaterial
                color="#fee2e2"
                opacity={0.6}
                transparent
            />
        </mesh>
    )
}

function StatusBadge({ status }: { status: string }) {
    const isConnected = status === "connected"

    const color =
        status === "connecting"
            ? "bg-amber-400"
            : isConnected
                ? "bg-emerald-500"
                : "bg-red-500"

    return (
        <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2 py-0.5 text-[11px]">
            <span className={`h-1.5 w-1.5 rounded-full ${color} animate-pulse`} />
            <span className="capitalize text-slate-700">{status || "idle"}</span>
        </span>
    )
}
