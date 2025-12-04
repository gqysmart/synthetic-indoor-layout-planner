'use client';

import { useGLTF } from "@react-three/drei";
import { Transform } from "@/lib/types/transform";
import * as THREE from "three";
import { use, useEffect } from "react";
import { useNormalizerModelBasedWidth } from "./useNormalizerModel";

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

export type FurnitureProps = {
    name: string;
    position?: [number, number];
    rotation?: number; // in radians
    width?: number;
    height?: number;
};


export function FurnitureModel3D({
    props,

}: {
    props?: FurnitureProps;
}) {

    console.log("Rendering FurnitureModel3D with props:", props);
    const name = props?.name || "";


    const defaultTransform: Transform = {
        position: [0, 0, 0],
        rotation: [0, 0, 0],
        scale: [1, 1, 1],
    };
    defaultTransform.position[0] = props?.position ? props.position[0] : 0;
    defaultTransform.position[2] = props?.position ? props.position[1] : 0;

    defaultTransform.rotation[1] = props?.rotation ? -props.rotation : 0;


    if (name.includes("BED") || name.includes("bed")) {
        console.log("Rendering bed model");
        const modelPath = getModelPath("bed");
        if (!modelPath) return null;
        return <BedModel3D safe_path={modelPath} size_width={Math.max(props?.width || 0.8, props?.height || 0.8)} transform={defaultTransform} />;
    } else if (name.includes("WARDROBE") || name.includes("wardrobe")) {
        console.log("Rendering wardrobe model");
        const modelPath = getModelPath("wardrobe");
        if (!modelPath) return null;
        return <WardrobeModel3D safe_path={modelPath} size_width={Math.max(props?.width || 0.8, props?.height || 0.8)} transform={defaultTransform} />;
    } else if (name.includes("DESK") || name.includes("desk") || name.includes("TABLE") || name.includes("table")) {
        console.log("Rendering desk model");
        const modelPath = getModelPath("desk");
        if (!modelPath) return null;
        return <DeskModel3D safe_path={modelPath} size_width={Math.max(props?.width || 0.8, props?.height || 0.8)} transform={defaultTransform} />;
    } else {
        console.log("No matching model for name:", name);
        const modelPath = getModelPath("desk");
        if (!modelPath) return null;
        return <DeskModel3D safe_path={modelPath} size_width={Math.max(props?.width || 0.8, props?.height || 0.8)} transform={defaultTransform} />;

        return null;
    }

    // switch (name) {
    //     case "bed":
    //         return <BedModel3D safe_path={modelPath} transform={defaultTransform} />;
    //     case "wardrobe":
    //         return <WardrobeModel3D safe_path={modelPath} transform={defaultTransform} />;
    //     case "desk":
    //         return <DeskModel3D safe_path={modelPath} transform={defaultTransform} />;
    //     default:
    //         return null;
}


export function BedModel3D({
    size_width,
    safe_path,
    transform,
}: {
    size_width: number;
    safe_path: string;
    transform: Transform;
}) {



    const gltf = useGLTF(safe_path);
    console.log("Before useNormalizer called BedModel3D size_width:", size_width);
    useNormalizerModelBasedWidth(gltf.scene, size_width, [transform.position[0], transform.position[2]], transform.rotation[1] + Math.PI / 2);

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
        // position={[
        //     transform.position[0],
        //     transform.position[1],
        //     transform.position[2],
        // ]}
        // rotation={transform.rotation}
        // scale={transform.scale}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}
export function WardrobeModel3D({
    size_width,
    safe_path,
    transform,
}: {
    size_width: number;
    safe_path: string;
    transform: Transform;
}) {
    const gltf = useGLTF(safe_path);
    useNormalizerModelBasedWidth(gltf.scene, size_width, [transform.position[0], transform.position[2]], transform.rotation[1] + Math.PI);
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
        // position={[
        //     transform.position[0],
        //     transform.position[1],
        //     transform.position[2],
        // ]}
        // rotation={[transform.rotation[0], transform.rotation[1], transform.rotation[2]]}
        // scale={transform.scale.map(s => s * 0.5) as [number, number, number]}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}


export function DeskModel3D({
    size_width,
    safe_path,
    transform,
}: {
    size_width: number;
    safe_path: string;
    transform: Transform;
}) {


    const gltf = useGLTF(safe_path);
    console.log("DeskModel3D size_width:", size_width);
    useNormalizerModelBasedWidth(gltf.scene, size_width, [transform.position[0], transform.position[2]], transform.rotation[1] + Math.PI / 2);

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
    // const box = new THREE.Box3().setFromObject(gltf.scene);
    // const size = new THREE.Vector3();
    // box.getSize(size);

    return (
        <group
        // position={[
        //     transform.position[0],
        //     transform.position[1],
        //     transform.position[2],
        // ]}
        // rotation={[transform.rotation[0], transform.rotation[1], transform.rotation[2]]}
        // scale={transform.scale.map(s => s * 0.5) as [number, number, number]}
        >
            <primitive object={gltf.scene} />
        </group>
    );
}
