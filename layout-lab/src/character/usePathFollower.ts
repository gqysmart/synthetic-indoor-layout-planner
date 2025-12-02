// app/character/usePathFollower.ts
import { RefObject, useEffect, useRef } from 'react'
import { Group, Vector3 } from 'three'
import { useFrame } from '@react-three/fiber'
import type { PathPoint } from './types'

interface PathFollowerOptions {
  enabled?: boolean 
  speed?: number           // 每秒走多少单位距离
  loop?: boolean           // 是否循环
}

export function usePathFollower(
  groupRef: RefObject<Group | null>,
  path?: PathPoint[] | null,
  options: PathFollowerOptions = {}
) {
  const {
    enabled = true,
    speed = 0.6,   // 可以根据感觉调
    loop = true,
  } = options

  const segmentIndexRef = useRef(0)
  const segmentProgressRef = useRef(0) // 当前段内 0~1 的插值

  const vFromRef = useRef(new Vector3())
  const vToRef = useRef(new Vector3())
  const vPosRef = useRef(new Vector3())
  const vDirRef = useRef(new Vector3())
  const vLookRef = useRef(new Vector3())

  // path / enabled / speed 变化时，重置进度
  useEffect(() => {
    segmentIndexRef.current = 0
    segmentProgressRef.current = 0
  }, [path, enabled, speed, loop])

  useFrame((_, delta) => {
    if (!enabled) return
    const group = groupRef.current
    if (!group) return
    if (!path || path.length < 2) return

    let idx = segmentIndexRef.current
    let t = segmentProgressRef.current
    let remainingTime = delta

    const vFrom = vFromRef.current
    const vTo = vToRef.current
    const vPos = vPosRef.current
    const vDir = vDirRef.current
    const vLook = vLookRef.current

    while (remainingTime > 0 && idx < path.length - 1) {
      const from = path[idx]
      const to = path[idx + 1]

      const y = group.position.y
      vFrom.set(from[0], y, from[1])
      vTo.set(to[0], y, to[1])

      const dist = vFrom.distanceTo(vTo)
      if (dist < 1e-6) {
        // 段太短，直接跳下一段
        idx++
        t = 0
        continue
      }

      const duration = dist / speed // 这一段需要多少秒
      const dt = remainingTime / duration

      if (t + dt >= 1) {
        // 这一帧就能走完这一段（甚至有多余时间）
        remainingTime -= (1 - t) * duration
        t = 1
      } else {
        t += dt
        remainingTime = 0
      }

      vPos.lerpVectors(vFrom, vTo, t)
      group.position.copy(vPos)

      vDir.subVectors(vTo, vFrom)
      if (vDir.lengthSq() > 1e-6) {
        vDir.normalize()
        vLook.copy(vPos).add(vDir)
        group.lookAt(vLook)
      }

      if (t >= 1) {
        idx++
        t = 0
      }
    }

    // 走到路径终点以后的处理
    if (idx >= path.length - 1) {
      if (loop) {
        idx = 0
        t = 0
      } else {
        idx = path.length - 1
        t = 1
      }
    }

    segmentIndexRef.current = idx
    segmentProgressRef.current = t
  })
}
