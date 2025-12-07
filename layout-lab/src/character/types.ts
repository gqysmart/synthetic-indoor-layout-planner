// src/character/types.ts

export type PathPoint = [number, number]

export type CharacterMode = 'path' | 'manual' | 'mixed'

export interface CharacterProps {
  path?: PathPoint[]|null
  initialPosition?: [number, number]
  segmentDuration?: number  // 每一段 path 的时间（秒）
  speed?: number            // 人物移动速度（预留）
  mode?: CharacterMode
  modelUrl?: string
  loop?: boolean
}
