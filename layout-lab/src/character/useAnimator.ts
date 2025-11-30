// app/character/useAnimator.ts
import { RefObject, useEffect } from 'react'
import { AnimationClip, Group, LoopRepeat, Mesh } from 'three'
import { useAnimations } from '@react-three/drei'

export function useCharacterAnimator(
  scene: Group|null,
  animations: AnimationClip[],
  groupRef: RefObject<Group | null>,
) {
  console.log("useCharacterAnimator called");
  
  const { actions, names } = useAnimations(animations, groupRef)

  // 阴影 & 动画播放
  useEffect(() => {
    if (!scene) return
    if (!groupRef.current) return

    // 开启阴影
    scene.traverse(obj => {
      const mesh = obj as Mesh
      if (mesh.isMesh) {
        mesh.castShadow = true
        mesh.receiveShadow = true
      }
    })
 
    if (!names.length) return
    const actionName = names[0]
    const action = actions[actionName]
    if (!action) return
    action.reset().play()
    action.loop = LoopRepeat
  }, [scene, actions, names, groupRef])

 

}
