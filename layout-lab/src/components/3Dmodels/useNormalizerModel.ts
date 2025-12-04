// 归一化身高 + 贴地
import { useLayoutEffect,RefObject, useRef } from 'react'
import { Group, Box3, Vector3 } from 'three'

export function useNormalizerModelBasedWidth(groupRef: Group | null, targetWidth: number = 0.8, targetPosition:[number,number] = [0,0],targetTheta:number) {  
    const normallizeRef : RefObject<boolean> = useRef(false);

useLayoutEffect(() => {
        const g = groupRef
        if (!g) return
        if (normallizeRef.current) {
            console.log("Already normalized, skipping.");
            return;
        }
        console.log("Before useNormalizer called with targetWidth:", targetWidth);
       
        normallizeRef.current = true;

        // 确保世界矩阵是最新的
        g.updateWorldMatrix(true, true)

        const box = new Box3().setFromObject(g)
        const size = new Vector3()
        box.getSize(size)
        console.log("Current model size:", size);

        const currentWidth = Math.max(size.x ,size.z)|| 1
        console.log("Current model width (max of x and z):", currentWidth);
        
        const scale = targetWidth / currentWidth
        g.scale.setScalar(scale)

        box.setFromObject(g)
        const minY = box.min.y
        const newSize = new Vector3()
        box.getSize(newSize)
        console.log("Model size after scaling:", newSize);

        const [x0, z0] = [targetPosition[0], targetPosition[1]]
        g.position.set(x0, -minY, z0)
        g.rotation.set(0, targetTheta, 0)   
    }, [groupRef, targetWidth])

}


