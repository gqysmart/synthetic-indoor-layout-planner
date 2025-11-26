'use client';

import { useGLTF } from "@react-three/drei";
import { Transform } from "@/lib/types/transform";
import * as THREE from "three";
import { useEffect } from "react";

function getModelPath(name: string) {
    switch (name) {
        case "bed":
            return "/models/bed.glb";
        case "wardrobe":
            return "/models/high_poly_wardrobe.glb";
        case "desk":
            return "/models/antique_desk.glb";
        default:
            return null;
    }
}

const defaultTransform: Transform = {
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
};

export function FurnitureModel3D({
    name,
    transform = defaultTransform,
}: {
    name: string;
    transform?: Transform;
}) {
    const modelPath = getModelPath(name);
    if (!modelPath) return null;

    const gltf = useGLTF(modelPath);

    // ✅ 关键：让 glTF 里的每个 mesh 支持阴影
    useEffect(() => {
        gltf.scene.traverse((obj) => {
            const mesh = obj as THREE.Mesh;
            if (mesh.isMesh) {
                mesh.castShadow = true;
                mesh.receiveShadow = true; // 可选，看你要不要模型自己接阴影
            }
        });
    }, [gltf.scene]);

    // 你现在的贴地计算（可以后面慢慢调）
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const size = new THREE.Vector3();
    box.getSize(size);

    return (
        <group
            position={[
                transform.position[0],
                transform.position[1] - size.y / 1.4,
                transform.position[2] - 0.8,
            ]}
            rotation={transform.rotation}
            scale={transform.scale}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}


export function WardrobeModel3D({
    name,
    transform = defaultTransform,
}: {
    name: string;
    transform?: Transform;
}) {
    const modelPath = getModelPath(name);
    if (!modelPath) return null;

    const gltf = useGLTF(modelPath);

    // ✅ 关键：让 glTF 里的每个 mesh 支持阴影
    useEffect(() => {
        gltf.scene.traverse((obj) => {
            const mesh = obj as THREE.Mesh;
            if (mesh.isMesh) {
                mesh.castShadow = true;
                mesh.receiveShadow = true; // 可选，看你要不要模型自己接阴影
            }
        });
    }, [gltf.scene]);

    // 你现在的贴地计算（可以后面慢慢调）
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const size = new THREE.Vector3();
    box.getSize(size);

    return (
        <group
            position={[
                transform.position[0] - 1.2,
                transform.position[1],
                transform.position[2] - 1.5,
            ]}
            rotation={[transform.rotation[0], transform.rotation[1] + Math.PI / 2, transform.rotation[2]]}
            scale={transform.scale.map(s => s * 0.5) as [number, number, number]}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}


export function DeskModel3D({
    name,
    transform = defaultTransform,
}: {
    name: string;
    transform?: Transform;
}) {
    const modelPath = getModelPath(name);
    if (!modelPath) return null;

    const gltf = useGLTF(modelPath);

    // ✅ 关键：让 glTF 里的每个 mesh 支持阴影
    useEffect(() => {
        gltf.scene.traverse((obj) => {
            const mesh = obj as THREE.Mesh;
            if (mesh.isMesh) {
                mesh.castShadow = true;
                mesh.receiveShadow = true; // 可选，看你要不要模型自己接阴影
            }
        });
    }, [gltf.scene]);

    // 你现在的贴地计算（可以后面慢慢调）
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const size = new THREE.Vector3();
    box.getSize(size);

    return (
        <group
            position={[
                transform.position[0],
                transform.position[1] + 0.2,
                transform.position[2] + 1.6,
            ]}
            rotation={[transform.rotation[0], transform.rotation[1] - Math.PI / 2, transform.rotation[2]]}
            scale={transform.scale.map(s => s * 0.5) as [number, number, number]}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}
