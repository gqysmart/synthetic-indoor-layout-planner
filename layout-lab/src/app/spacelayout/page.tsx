'use client'

import { Canvas } from "@react-three/fiber"
import Link from "next/link"
import { Grid, OrbitControls } from "@react-three/drei"
import { FurnitureModel3D, FurnitureProps } from "@/components/3Dmodels/furniture3D"
import { Character } from "@/components/3Dmodels/character"
import { useMemo, useState, memo, useEffect, useCallback } from "react"
import { usePlannerSocket } from "@/hooks/usePlannerSocket"

import { LayoutDTO, WsIncomingMessage } from "@/lib/types/websocketMessage"
import { LayoutPreview } from "@/components/ui/layoutPreview"
// import pathRandom from "../spacelayout/testPath2"




export default function RoomLayoutPage() {
    // const [room] = useState<Room>("beadroom");
    // const [furnitures] = useState<Furniture[]>(["bed", "desk", "wardrobe"]);
    // const [algorithm] = useState("csp");

    const [wsUrl, setWsUrl] = useState<string | null>(null);
    const [path, setPath] = useState<[number, number][] | null>([]);
    const [data_layout, set_data_layout] = useState<LayoutDTO[] | null>([]);
    /* for show which layout we want to use */
    const [selected, set_selected] = useState<number | null>(null);
    /* list the algorithms */
    const algorithms = ["csp", "A*"];
    const [algorithm_selected, set_algorithm_selected] = useState<number>(0);


    const context_selected_layout: RoomLayoutContext = {
        layout_selected: selected,
        layouts: data_layout,
        algorithm: algorithms[algorithm_selected],
        path: path,

    };

    const url_for_jobId = "/api/plan/jobs";

    const handlePlannerMessage = useCallback((msg: WsIncomingMessage) => {
        if (msg.type === "status") {
            console.log("Websocket Status update:", msg.payload?.message);
        } else if (msg.type === "error") {
            console.error("Error from websocket server:", msg.payload?.message);
        } else if (msg.type === "path_response") {
            if (msg.payload?.command === "start_path_finding") {
                setPath(msg.payload.path);
            }
            console.log("Response from websocket server:", msg.payload);
        }
        else if (msg.type === "layout_response") {
            if (msg.payload?.command === "get_example_layout") {
                const layout = msg.payload.layout;
                console.log("Received example layout:", layout);
                set_data_layout(layout);
                if (layout.length > 0) {
                    set_selected(0);//default selct the first one
                }
            }
        }
    }, []);

    const { status, startSocket, sendCommand, stopSocket } =
        usePlannerSocket(handlePlannerMessage);

    useEffect(() => {
        // Example: Fetch a new job ID from the server when the component mounts
        async function fetchWS() {
            // Replace with your actual API call
            const response = await fetch(url_for_jobId, { method: 'POST' });
            const data = await response.json();
            if (!data.server_url) {
                console.error("Invalid response:", data);
            } else {
                setWsUrl(data.server_url);

            }
        }
        fetchWS();
    }, []);

    useEffect(() => {
        if (!wsUrl) return;
        console.log("Starting websocket with url:", wsUrl);
        startSocket(wsUrl);
        return () => {
            // 组件卸载时关闭连接
            stopSocket();
        }
    }, [wsUrl, startSocket, stopSocket]);



    // const roomContext: RoomLayoutContext = useMemo(() => ({
    //     room,
    //     furnitures,
    //     algorithm,
    //     path,
    // }), [room, furnitures, algorithm, path]);

    return (
        <main className="h-screen bg-slate-950 text-slate-50 flex flex-col">
            {/* Header */}
            <header className="h-14 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-900/80 backdrop-blur">
                <div className="flex items-center gap-3">
                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20 text-blue-300 text-sm font-semibold">
                        LL
                    </span>
                    <div>
                        <h1 className="text-sm font-semibold tracking-wide">
                            Layout Lab
                        </h1>
                        <p className="text-xs text-slate-400">
                            Synthetic Indoor Layout Planner
                        </p>
                    </div>
                </div>

                <nav className="text-xs text-slate-400 flex items-center gap-4">
                    <Link href="/" className="hover:text-slate-200 transition">
                        Home
                    </Link>
                    <span className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded-full bg-slate-800/70 border border-slate-700/80">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        Live 3D
                    </span>
                </nav>
            </header>

            {/* Main Content */}
            <section className="flex-1 flex min-h-0">
                {/* Sidebar */}
                <aside className="w-72 border-r border-slate-800 p-4 bg-slate-900/80 backdrop-blur-sm overflow-y-auto">
                    <h2 className="text-xs font-semibold tracking-wide text-slate-300 mb-3 uppercase">
                        Layout Control
                    </h2>

                    {/* Connection card */}
                    <div className="mb-4 rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-xs space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-200">WebSocket</span>
                            <StatusBadge status={status} />
                        </div>
                        <p className="text-[11px] text-slate-400 break-all leading-relaxed">
                            {wsUrl ?? "Waiting for server URL…"}
                        </p>
                        <button
                            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800/80 text-[11px] py-1.5 hover:bg-slate-700 transition disabled:opacity-50"
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
                    </div>

                    {/* Layout selection card */}
                    <div className="mb-4 rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-xs space-y-2">
                        <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-slate-200">Layouts</span>
                            <span className="text-[11px] text-slate-400">
                                {data_layout?.length ?? 0} loaded
                            </span>
                        </div>

                        <label className="block text-[11px] text-slate-400 mb-1">
                            Choose layout
                        </label>
                        <select
                            value={selected !== null ? String(selected) : ""}
                            onChange={(e) =>
                                set_selected(
                                    e.target.value === "" ? null : Number(e.target.value)
                                )
                            }
                            className="w-full mb-2 border border-slate-700 bg-slate-900/80 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">Select a layout…</option>
                            {data_layout?.map((layout, index) => (
                                <option key={layout.name} value={index}>
                                    {layout.name}
                                </option>
                            ))}
                        </select>

                        <div className="rounded-lg border border-slate-800 bg-slate-950/40 overflow-hidden">
                            <LayoutPreview
                                layout={
                                    selected !== null && data_layout ? data_layout[selected] : null
                                }
                            />
                        </div>
                    </div>

                    {/* Algorithm + actions card */}
                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-xs space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-200">Path finding</span>
                            <span className="text-[11px] text-slate-500">
                                Algorithm
                            </span>
                        </div>

                        <select
                            className="w-full border border-slate-700 bg-slate-900/80 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
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
                            className="w-full mt-1 rounded-lg bg-emerald-500 text-emerald-950 text-[11px] font-medium py-1.5 hover:bg-emerald-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
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
                            <p className="text-[11px] text-emerald-300 mt-1">
                                Path loaded: {path.length} points
                            </p>
                        )}
                    </div>
                </aside>

                {/* 3D Viewport */}
                <section className="flex-1 flex flex-col min-h-0 bg-slate-950">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-900/80 backdrop-blur">
                        <div>
                            <h2 className="text-xs font-semibold text-slate-200 tracking-wide uppercase">
                                3D Viewport
                            </h2>
                            <p className="text-[11px] text-slate-400">
                                Room:{" "}
                                {selected !== null && data_layout
                                    ? data_layout[selected].room.name ?? "Unnamed"
                                    : "No layout selected"}
                            </p>
                        </div>
                        <div className="text-[11px] text-slate-400">
                            Algo:{" "}
                            <span className="text-slate-200 font-medium">
                                {algorithms[algorithm_selected]}
                            </span>
                        </div>
                    </div>

                    <Canvas
                        shadows
                        dpr={[1, 2]}
                        camera={{ position: [5, 5, 5], fov: 50 }}
                        className="flex-1 bg-slate-950"
                    >
                        <LayoutScene context={context_selected_layout} />
                    </Canvas>

                    <footer className="mt-auto py-3 text-center text-[11px] text-slate-500 border-t border-slate-800 bg-slate-900/80">
                        © 2025 ACE AI · Layout Lab
                    </footer>
                </section>
            </section>
        </main>
    )


}

type RoomLayoutContext = {
    path: [number, number][] | null,
    layout_selected: number | null,
    layouts: LayoutDTO[] | null,
    algorithm: string | null,

}

const LayoutScene = memo(function LayoutScene({ context }: { context: RoomLayoutContext }) {
    const { path, algorithm, layouts, layout_selected } = context;
    console.log("Rendering LayoutScene with context:", context);

    return (
        <>
            {/* 背景颜色：改成偏浅的灰色 */}
            <color attach="background" args={["#f4f4f5"]} />

            {/* 环境光加强一点 */}
            <ambientLight intensity={0.8} />

            {/* 半球光：模拟天空/地面反射，让物体不那么黑 */}
            <hemisphereLight
                skyColor="#ffffff"
                groundColor="#dddddd"
                intensity={0.6}
            />

            {/* 定向光：做出阴影和立体感 */}
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

            {/* Fog 可以弱一点，避免远处全白/全灰 */}
            <fog attach="fog" args={["#e5e7eb", 30, 160]} />

            {/* 加一个 Grid, 让空间感更强 */}
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
                    {/* 底色也不要太黑 */}
                    <meshStandardMaterial color="#e5e7eb" />
                </mesh>
            )}
        </>
    )
})


const RoomAndFurnitures = memo(function RoomAndFurnitures({ layouts, selected, path }: { layouts: LayoutDTO[], selected: number, path: [number, number][] | null }) {
    console.log("Rendering RoomAndFurnitures with selected layout:", layouts[selected]);
    const layout = layouts[selected];
    const furnitures = layout.furnitures;
    return (

        <>

            <Room width={layout.room.width} height={layout.room.height} />
            {
                furnitures.map((furniture, idx) =>
                    <FurnitureModel3D key={idx} props={{ name: furniture.type, position: [furniture.position[0], furniture.position[1]], rotation: furniture.rotation }} />
                )
            }

        </>
    )
})

function Room({ width, height }: { width: number, height: number }) {
    return (
        <mesh
            receiveShadow
            rotation={[-Math.PI / 2, 0, 0]}
            position={[0, 0, 0]}
        >
            <planeGeometry args={[width, height]} />
            <meshStandardMaterial
                color="#ffe4ea"      // 比较浅的粉色
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
                ? "bg-emerald-400"
                : "bg-red-500"

    return (
        <span className="inline-flex items-center gap-1 rounded-full bg-slate-800/80 border border-slate-700 px-2 py-0.5 text-[11px]">
            <span className={`h-1.5 w-1.5 rounded-full ${color} animate-pulse`} />
            <span className="capitalize text-slate-200">{status || "idle"}</span>
        </span>
    )
}
