import { useGLTF } from '@react-three/drei'
import { useEffect, useRef } from 'react'
import { Group } from 'three'
import { useNormalizer } from './useNormalizer'
import { useCharacterAnimator } from './useAnimator'
import { useKeyboardController } from './useKeyboardController'
import { CharacterProps } from './types'
import { usePathFollower } from './usePathFollower'
// import { usePathFollower } from './usePathFollower'

export function Character({
    path = [],
    initialPosition = [0, 0],
    segmentDuration = 0.5,
    speed = 1,
    mode = 'mixed',
    modelUrl = '/models/personaje_rs.glb',
}: CharacterProps) {
    const groupRef = useRef<Group>(null)
    console.log("Character render with modelUrl:", path)

    // 1) useGLTF 是 Suspense hook，本身就会“延迟”渲染
    const { scene, animations } = useGLTF(modelUrl)

    // 2) 无论如何，每次 render 都调用 useAnimations

    // 3) 所有依赖 ref / animations 的操作都放在 effect 里ss
    useNormalizer(groupRef, 0.8)
    useCharacterAnimator(scene, animations, groupRef)

    const pathFollowerEnabled = mode === 'path' || mode === 'mixed'
    const keyboardEnabled = mode === 'manual' || mode === 'mixed'

    useEffect(() => {
        if (!groupRef.current || !initialPosition) return
        const [x, z] = initialPosition
        groupRef.current.position.set(x, groupRef.current.position.y, z)
    }, [initialPosition])

    // 路径跟随
    // usePathFollower(groupRef, path, {
    //     enabled: pathFollowerEnabled,
    //     segmentDuration,
    // })
    usePathFollower(groupRef, path, {
        enabled: pathFollowerEnabled,
        speed,
    })

    // 键盘控制
    useKeyboardController(groupRef, {
        enabled: keyboardEnabled,
        speed,
    })

    // // 没有路径时，如果 mode 是纯 path，可以选择不渲染
    // if (mode === 'path' && (!path || path.length === 0)) {
    //     return null
    // }

    return (
        <group ref={groupRef}>
            <primitive object={scene} />
        </group>
    )


    // return <primitive object={scene} ref={groupRef} />
}
