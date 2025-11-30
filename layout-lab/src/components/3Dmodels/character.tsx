// 'use client'

// import { useRef, useEffect, useLayoutEffect } from 'react'
// import { useGLTF, useAnimations } from '@react-three/drei'
// import { Group, Box3, Vector3, LoopRepeat, Mesh } from 'three'
// import { useFrame } from '@react-three/fiber'
// import { useNormalizer } from '@/character/useNormalizer'
// import { useKeyboardController } from '@/character/useKeyboardController'

// const KEY_MAP = {
//     KeyW: 'forward',
//     KeyS: 'backward',
//     KeyA: 'left',
//     KeyD: 'right',
// } as const

// type MoveKey = (typeof KEY_MAP)[keyof typeof KEY_MAP]

// export function Character() {
//     const group = useRef<Group>(null)

//     const path = '/models/personaje_rs.glb'
//     const { scene, animations } = useGLTF(path)
//     const { actions, names } = useAnimations(animations, group)

//     const pressed = useRef<Record<MoveKey, boolean>>({
//         forward: false,
//         backward: false,
//         left: false,
//         right: false,
//     })

//     // 播放动画 + 开启阴影
//     useEffect(() => {
//         if (!names.length) return

//         scene.traverse((obj) => {
//             const mesh = obj as Mesh
//             if (mesh.isMesh) {
//                 mesh.castShadow = true
//                 mesh.receiveShadow = true
//             }
//         })

//         const actionName = names[0]
//         const action = actions[actionName]
//         if (!action) return

//         action.reset().play()
//         action.loop = LoopRepeat
//     }, [actions, names, scene])

//     // ⭐ 归一化身高 + 贴地（带日志）
//     // useLayoutEffect(() => {
//     //     if (!group.current) {
//     //         console.log('[Character] group.current 还是 null，跳过缩放')
//     //         return
//     //     }

//     //     // 确保世界矩阵是最新的
//     //     group.current.updateWorldMatrix(true, true)

//     //     const box = new Box3().setFromObject(group.current)
//     //     const size = new Vector3()
//     //     box.getSize(size)

//     //     const currentHeight = size.y || 1
//     //     const targetHeight = 0.1

//     //     const scale = targetHeight / currentHeight

//     //     console.log('[Character] bbox height:', currentHeight, 'scale:', scale)

//     //     // 先不要 *0.5，方便你肉眼确认变化
//     //     group.current.scale.setScalar(scale)
//     //     // 暂时改成这样测试：
//     //     // group.current.scale.setScalar(0.1)

//     //     // 重新算一遍包围盒，让脚贴地
//     //     box.setFromObject(group.current)
//     //     const minY = box.min.y

//     //     const x0 = -0.5
//     //     const z0 = 0
//     //     group.current.position.set(x0, -minY, z0)
//     // }, [scene])
//     useNormalizer(group, 0.8)

//     // 键盘监听
//     // useEffect(() => {
//     //     const handleKeyDown = (e: KeyboardEvent) => {
//     //         if (!(e.code in KEY_MAP)) return
//     //         const key = KEY_MAP[e.code as keyof typeof KEY_MAP]
//     //         pressed.current[key] = true
//     //     }

//     //     const handleKeyUp = (e: KeyboardEvent) => {
//     //         if (!(e.code in KEY_MAP)) return
//     //         const key = KEY_MAP[e.code as keyof typeof KEY_MAP]
//     //         pressed.current[key] = false
//     //     }

//     //     window.addEventListener('keydown', handleKeyDown)
//     //     window.addEventListener('keyup', handleKeyUp)
//     //     return () => {
//     //         window.removeEventListener('keydown', handleKeyDown)
//     //         window.removeEventListener('keyup', handleKeyUp)
//     //     }
//     // }, [])
//     useKeyboardController(group, {
//         enabled: true,
//         speed: 1,
//     })

//     // useFrame((_, delta) => {
//     //     const g = group.current
//     //     if (!g) return

//     //     const speed = 1.2

//     //     let dx = 0
//     //     let dz = 0

//     //     if (pressed.current.forward) dz -= speed * delta
//     //     if (pressed.current.backward) dz += speed * delta
//     //     if (pressed.current.left) dx -= speed * delta
//     //     if (pressed.current.right) dx += speed * delta

//     //     if (dx !== 0 || dz !== 0) {
//     //         g.position.x += dx
//     //         g.position.z += dz

//     //         const halfWidth = 3 / 2
//     //         const halfDepth = 4 / 2
//     //         const margin = 0.2

//     //         g.position.x = Math.min(
//     //             Math.max(g.position.x, -halfWidth + margin),
//     //             halfWidth - margin,
//     //         )
//     //         g.position.z = Math.min(
//     //             Math.max(g.position.z, -halfDepth + margin),
//     //             halfDepth - margin,
//     //         )
//     //     }
//     // })

//     return (
//         <group ref={group}>
//             <primitive object={scene} />
//         </group>
//     )
// }

// useGLTF.preload('/models/personaje_rs.glb')
export { Character } from '@/character/Character'