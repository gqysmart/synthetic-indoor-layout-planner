// app/character/useKeyboardController.ts
import {  RefObject, useEffect, useRef } from 'react'
import { Group, Vector3 } from 'three'
import { useFrame } from '@react-three/fiber'

const KEY_MAP = {
  KeyW: 'forward',
  KeyS: 'backward',
  KeyA: 'left',
  KeyD: 'right',
} as const

type MoveKey = (typeof KEY_MAP)[keyof typeof KEY_MAP]

const vDir = new Vector3()
const vLook = new Vector3()

interface KeyboardControllerOptions {
  enabled?: boolean
  speed?: number
  // 可选：边界限制
  bounds?: {
    halfWidth: number
    halfDepth: number
    margin: number
  }
}

export function useKeyboardController(
  groupRef: RefObject<Group | null>,
  options: KeyboardControllerOptions = {}
) {
  const {
    enabled = true,
    speed = 1.2,
    bounds = {
      halfWidth: 3 / 2, // 3m 宽
      halfDepth: 4 / 2, // 4m 深
      margin: 0.2,
    },
  } = options

  // 当前按键状态
  const pressed = useRef<Record<MoveKey, boolean>>({
    forward: false,
    backward: false,
    left: false,
    right: false,
  })

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const code = e.code as keyof typeof KEY_MAP
      if (!(code in KEY_MAP)) return
      const key = KEY_MAP[code]
      pressed.current[key] = true
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      const code = e.code as keyof typeof KEY_MAP
      if (!(code in KEY_MAP)) return
      const key = KEY_MAP[code]
      pressed.current[key] = false
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  useFrame((_, delta) => {
    if (!enabled) return
    const g = groupRef.current
    if (!g) return

    let dx = 0
    let dz = 0

    if (pressed.current.forward) dz -= speed * delta
    if (pressed.current.backward) dz += speed * delta
    if (pressed.current.left) dx -= speed * delta
    if (pressed.current.right) dx += speed * delta

    if (dx !== 0 || dz !== 0) {
      g.position.x += dx
      g.position.z += dz

      // 限制在房间内
      const { halfWidth, halfDepth, margin } = bounds
      g.position.x = Math.min(
        Math.max(g.position.x, -halfWidth + margin),
        halfWidth - margin,
      )
      g.position.z = Math.min(
        Math.max(g.position.z, -halfDepth + margin),
        halfDepth - margin,
      )

      // 面向移动方向
      vDir.set(dx, 0, dz).normalize()
      vLook.copy(g.position).add(vDir)
      g.lookAt(vLook)
    }
  })
}
