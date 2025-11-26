'use client'

import { Canvas } from "@react-three/fiber"
import Link from "next/link"
import { Grid, OrbitControls } from "@react-three/drei"
import { FurnitureModel3D, WardrobeModel3D, DeskModel3D } from "@/components/3Dmodels/furniture3D"
import { Transform } from "@/lib/types/transform"
import { Character } from "@/components/3Dmodels/character"

export default function RoomLayoutPage() {

    return (
        <main className="h-screen bg-slate-50 flex flex-col">
            <header className="invisible h-16 flex items-center px-4 border">
                <h1>Layout Lab</h1>
                <nav className="ml-4">
                    <Link href="/">Home</Link>
                </nav>
            </header>

            <section className="flex-1 flex">
                <aside className="w-64 border-r p-4 overflow-y-auto">
                    <ul className="space-y-6 text-sm">
                        <li className="space-y-2">
                            <p className="font-medium">Change Room</p>
                            <select className="w-full border p-2 rounded">
                                <option>Living Room</option>
                                <option>Bedroom</option>
                                <option>Office</option>
                            </select>
                            <p className="text-gray-600">room information</p>

                        </li>
                        <li className="space-y-2">
                            <p className="font-medium">Add Furniture</p>
                            <select className="w-full border p-2 rounded">
                                <option>Sofa</option>
                                <option>Table</option>
                                <option>Chair</option>
                            </select>
                            <button className="w-full  bg-blue-500 text-white rounded px-4 py-2">Add</button>
                            <p className="text-gray-600">furniture information</p>
                            <hr />
                            <p className="font-medium">Added Furnitures</p>
                            <select className="w-full border p-2 rounded">
                                <option>Sofa</option>
                                <option>Table</option>
                                <option>Chair</option>
                            </select>
                            <button className="w-full bg-green-600 text-white rounded p-2">Remove</button>
                        </li>
                        <li className="space-y-2">
                            <p className="font-medium">layout options</p>
                            <select className="w-full border p-2 rounded">
                                <option>Optimize Space</option>
                                <option>Maximize Comfort</option>
                                <option>Custom</option>
                            </select>
                            <button className="w-full bg-green-600 text-white rounded p-2">Generate Layout</button>
                        </li>
                    </ul>
                </aside>

                <section className="flex-1 flex flex-col min-h-0" >
                    <h2 className="text-xl font-semibold 
                     px-4 py-2 border-b bg-white/70 backdrop-blur">
                        3D Viewport
                    </h2>
                    <Canvas shadows dpr={[1, 2]} camera={{ position: [5, 5, 5], fov: 50 }} className="flex-1 bg-white" >
                        <LayoutScene algorithm="hybrid" />
                    </Canvas>
                </section>
            </section>
            <footer className='mt-auto py-6 text-center text-gray-200 border-t'>
                <p> © 2025 ACE AI. All rights reserved. </p>
            </footer>
        </main>
    )

}
type Algorithm = "bfs" | "csp" | "hybrid";
function LayoutScene({ algorithm = "csp" }: { algorithm?: Algorithm }) {
    const roomColor =
        algorithm === "csp"
            ? "#6b7280" // slate-500
            : algorithm === "bfs"
                ? "#0f766e" // teal-700
                : "#7c3aed"; // violet-600

    return (
        <>
            <ambientLight intensity={0.5} />
            <directionalLight
                position={[5, 10, 5]}
                intensity={1.2}
                shadow-mapSize-width={2048}
                shadow-mapSize-height={2048}
                castShadow />

            {/* <mesh
                rotation={[-Math.PI / 2, 0, 0]}
                receiveShadow>
                <planeGeometry args={[4, 5]} />
                <meshStandardMaterial
                    color={roomColor}
                    opacity={0.35}
                    transparent
                />
            </mesh> */}
            <mesh
                receiveShadow
                rotation={[-Math.PI / 2, 0, 0]}
                position={[0, 0, 0]}
            >
                <planeGeometry args={[3, 4]} />
                <meshStandardMaterial color="#dddddd" />
                {/* <shadowMaterial transparent opacity={0.4} /> */}
            </mesh>
            {/* <mesh>
                <planeGeometry args={[3, 4]} />
                <meshStandardMaterial color="#a78bfa" transparent opacity={0.5} />
                <meshBasicMaterial color="#5b21b6" wireframe />
            </mesh> */}
            <FurnitureModel3D
                name="bed"
            />
            <DeskModel3D
                name="desk"
            />
            <WardrobeModel3D
                name="wardrobe"
            />

            <Character />


            <Grid
                position={[0, -0.02, 0]}
                args={[10, 10]}
                cellSize={0.5}
                cellThickness={0.5}
                infiniteGrid
                fadeDistance={30}
                fadeStrength={1}
            />

            <OrbitControls
                enablePan
                enableZoom
                enableRotate
                target={[0, 0.4, 0]}
                maxPolarAngle={Math.PI / 2.1}
            />
            <fog attach="fog" args={["#ffffff", 20, 120]} />
        </>
    )
}

