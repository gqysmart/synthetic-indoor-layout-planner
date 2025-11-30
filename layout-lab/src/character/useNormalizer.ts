// 归一化身高 + 贴地
import { useLayoutEffect,RefObject, useRef } from 'react'
import { Group, Box3, Vector3 } from 'three'

export function useNormalizer(groupRef: RefObject<Group | null>, targetHeight: number = 0.8)    {  
    const normallizeRef : RefObject<boolean> = useRef(false);

useLayoutEffect(() => {
        console.log("useNormalizer called with targetHeight:", targetHeight);
        const g = groupRef.current
        if (!g) return
        if (normallizeRef.current) {
            console.log("Already normalized, skipping.");
            return;
        }
        normallizeRef.current = true;

        // 确保世界矩阵是最新的
        g.updateWorldMatrix(true, true)

        const box = new Box3().setFromObject(g)
        const size = new Vector3()
        box.getSize(size)

        const currentHeight = size.y || 1
        
        const scale = targetHeight / currentHeight
        g.scale.setScalar(scale)

        box.setFromObject(g)
        const minY = box.min.y

        const [x0, z0] = [g.position.x, g.position.z]
        g.position.set(x0, -minY, z0)
    }, [groupRef, targetHeight])

}
