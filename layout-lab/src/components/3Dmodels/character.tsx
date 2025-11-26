'use client'

import { useRef, useEffect, useLayoutEffect } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { Group, Box3, Vector3, LoopRepeat, Mesh } from 'three'
import { useFrame } from '@react-three/fiber'

const KEY_MAP = {
    KeyW: 'forward',
    KeyS: 'backward',
    KeyA: 'left',
    KeyD: 'right',
} as const

type MoveKey = (typeof KEY_MAP)[keyof typeof KEY_MAP]

export function Character() {
    const group = useRef<Group>(null)

    const path = '/models/personaje_rs.glb'
    const { scene, animations } = useGLTF(path)
    const { actions, names } = useAnimations(animations, group)

    // 当前按键状态
    const pressed = useRef<Record<MoveKey, boolean>>({
        forward: false,
        backward: false,
        left: false,
        right: false,
    })

    // 播放动画 + 开启阴影
    useEffect(() => {
        if (!names.length) return

        // 模型所有 mesh 开启阴影
        scene.traverse((obj) => {
            const mesh = obj as Mesh
            if (mesh.isMesh) {
                mesh.castShadow = true
                mesh.receiveShadow = true
            }
        })

        const actionName = names[0]
        const action = actions[actionName]
        if (!action) return

        action.reset().play()
        action.loop = LoopRepeat
    }, [actions, names, scene])

    // 键盘监听
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!(e.code in KEY_MAP)) return;   // ⭐ 类型收窄

            const key = KEY_MAP[e.code as keyof typeof KEY_MAP];
            pressed.current[key] = true;
        }


        const handleKeyUp = (e: KeyboardEvent) => {
            if (!(e.code in KEY_MAP)) return;

            const key = KEY_MAP[e.code as keyof typeof KEY_MAP];
            pressed.current[key] = false;
        }


        window.addEventListener('keydown', handleKeyDown)
        window.addEventListener('keyup', handleKeyUp)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
            window.removeEventListener('keyup', handleKeyUp)
        }
    }, [])

    // 归一化身高 + 贴地
    useLayoutEffect(() => {
        if (!group.current) return

        // 1) 以原始模型尺寸计算当前高度
        const box = new Box3().setFromObject(group.current)
        const size = new Vector3()
        box.getSize(size)

        const currentHeight = size.y || 1
        const targetHeight = 1.7 // 目标人物身高（米）

        const scale = targetHeight / currentHeight
        group.current.scale.setScalar(scale * 0.5)

        // 2) 缩放后重新计算包围盒，让脚贴在 y = 0 平面上
        box.setFromObject(group.current)
        const minY = box.min.y

        // 初始水平位置你可以改（比如 [-0.5, 0, 0]）
        const x0 = -0.5
        const z0 = 0

        group.current.position.set(x0, -minY, z0)
    }, [scene])

    // 每帧根据键盘移动人物
    useFrame((_, delta) => {
        const g = group.current
        if (!g) return

        const speed = 1.2 // m/s

        let dx = 0
        let dz = 0

        if (pressed.current.forward) dz -= speed * delta
        if (pressed.current.backward) dz += speed * delta
        if (pressed.current.left) dx -= speed * delta
        if (pressed.current.right) dx += speed * delta

        if (dx !== 0 || dz !== 0) {
            g.position.x += dx
            g.position.z += dz

            // 房间平面是 3×4，中心在原点：
            // x ∈ [-1.5, 1.5], z ∈ [-2, 2]
            const halfWidth = 3 / 2
            const halfDepth = 4 / 2
            const margin = 0.2 // 离墙留一点距离

            g.position.x = Math.min(Math.max(g.position.x, -halfWidth + margin), halfWidth - margin)
            g.position.z = Math.min(Math.max(g.position.z, -halfDepth + margin), halfDepth - margin)
        }
    })

    return (
        <group ref={group}>
            <primitive object={scene} />
        </group>
    )
}

// 预加载（可选）
useGLTF.preload('/models/personaje_rs.glb')
