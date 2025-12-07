// app/character/usePathFollower.ts
import { RefObject, useEffect, useRef } from 'react'
import { Group, Vector3 } from 'three'
import { useFrame } from '@react-three/fiber'
import type { PathPoint } from './types'

interface PathFollowerOptions {
  enabled?: boolean
  speed?: number     // 每秒走多少单位
  loop?: boolean
}

export function usePathFollower(
  groupRef: RefObject<Group | null>,
  path?: PathPoint[] | null,
  options: PathFollowerOptions = {}
) {
  const {
    enabled = true,
    speed = 0.6,
    loop = true,
  } = options

  // 当前在走的段索引 [i -> i+1]
  const segmentIndexRef = useRef(0)
  // 当前段已经走了多少距离（不是 0~1，而是 0~segmentLength）
  const distanceOnSegmentRef = useRef(0)

  const vFromRef = useRef(new Vector3())
  const vToRef = useRef(new Vector3())
  const vPosRef = useRef(new Vector3())
  const vDirRef = useRef(new Vector3())
  const vLookRef = useRef(new Vector3())

  // 当 path / enabled / speed / loop 变化时重置
  useEffect(() => {
    segmentIndexRef.current = 0
    distanceOnSegmentRef.current = 0
  }, [path, enabled, speed, loop])

  useFrame((_, delta) => {
    if (!enabled) return
    const group = groupRef.current
    if (!group) return
    if (!path || path.length < 2) return

    let idx = segmentIndexRef.current
    let dOnSeg = distanceOnSegmentRef.current

    let remainDist = speed * delta // 本帧还能走多少距离

    const vFrom = vFromRef.current
    const vTo = vToRef.current
    const vPos = vPosRef.current
    const vDir = vDirRef.current
    const vLook = vLookRef.current

    const y = group.position.y

    while (remainDist > 0 && idx < path.length - 1) {
      const [x1, z1] = path[idx]
      const [x2, z2] = path[idx + 1]

      vFrom.set(x1, y, z1)
      vTo.set(x2, y, z2)

      const segLen = vFrom.distanceTo(vTo)
      if (segLen < 1e-6) {
        // 段太短，直接跳过
        idx++
        dOnSeg = 0
        continue
      }

      const segRemain = segLen - dOnSeg

      if (remainDist < segRemain) {
        // 这一帧走不完这一段
        dOnSeg += remainDist
        const t = dOnSeg / segLen
        vPos.lerpVectors(vFrom, vTo, t)
        remainDist = 0
      } else {
        // 这一帧走完这一段，还有富余距离
        remainDist -= segRemain
        dOnSeg = 0
        idx++
        vPos.copy(vTo)
      }

      group.position.copy(vPos)

      // 方向 & 旋转
      vDir.subVectors(vTo, vFrom)
      if (vDir.lengthSq() > 1e-6) {
        vDir.normalize()
        vLook.copy(vPos).add(vDir)
        group.lookAt(vLook)
      }
    }

    // 处理到达终点
    if (idx >= path.length - 1) {
      if (loop) {
        idx = 0
        dOnSeg = 0
      } else {
        // 停在最后一个点
        const [xLast, zLast] = path[path.length - 1]
        group.position.set(xLast, group.position.y, zLast)
        segmentIndexRef.current = path.length - 1
        distanceOnSegmentRef.current = 0
        return
      }
    }

    segmentIndexRef.current = idx
    distanceOnSegmentRef.current = dOnSeg
  })
}
