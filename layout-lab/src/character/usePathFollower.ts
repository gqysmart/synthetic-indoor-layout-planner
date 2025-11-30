// app/character/usePathFollower.ts
import { RefObject, useEffect, useRef } from 'react'
import { Group, Vector3 } from 'three'
import { useFrame } from '@react-three/fiber'
import type { PathPoint } from './types'

interface PathFollowerOptions {
  enabled?: boolean
  segmentDuration?: number // 每一段走多久（秒）
}

export function usePathFollower(
  groupRef: RefObject<Group | null>,
  path?: PathPoint[] | null,
  options: PathFollowerOptions = {}
) {
  const { enabled = true, segmentDuration = 2 } = options

  // 当前在走第几段 [i -> i+1]
  const segmentIndexRef = useRef(0)
  // 当前段已经走了多少秒
  const segmentTimeRef = useRef(0)

  // 每个 follower 自己的一组向量，避免模块级全局变量共享
  const vFromRef = useRef(new Vector3())
  const vToRef = useRef(new Vector3())
  const vPosRef = useRef(new Vector3())
  const vDirRef = useRef(new Vector3())
  const vLookRef = useRef(new Vector3())

  // 当 path / enabled / segmentDuration 变化时，重置进度
  useEffect(() => {
    segmentIndexRef.current = 0
    segmentTimeRef.current = 0
  }, [path, enabled, segmentDuration])

  useFrame((_, delta) => {
    if (!enabled) return
    const group = groupRef.current
    if (!group) return
    if (!path || path.length < 2) return

    const vFrom = vFromRef.current
    const vTo = vToRef.current
    const vPos = vPosRef.current
    const vDir = vDirRef.current
    const vLook = vLookRef.current

    let idx = segmentIndexRef.current
    if (idx >= path.length - 1) {
      idx =0
      
    }

    // 1. 累加当前段时间
    segmentTimeRef.current += delta
    let t = segmentTimeRef.current / segmentDuration
    if (t > 1) t = 1

    const from = path[idx]
    const to = path[idx + 1]

    // 2. 生成 from / to 位置（这里假设 PathPoint 是 [x, z]）
    const y = group.position.y
    vFrom.set(from[0], y, from[1])
    vTo.set(to[0], y, to[1])

    // 3. 插值移动
    vPos.lerpVectors(vFrom, vTo, t)
    group.position.copy(vPos)

    // 4. 朝向（防止 0 向量导致 NaN）
    vDir.subVectors(vTo, vFrom)
    if (vDir.lengthSq() > 1e-6) {
      vDir.normalize()
      vLook.copy(vPos).add(vDir)
      group.lookAt(vLook)
    }

    // 5. 当前段走完 → 切下一段
    if (t >= 1) {
      segmentIndexRef.current = idx + 1
      segmentTimeRef.current = 0
    }
  })
}
