export interface Dance {
  id: number
  name: string
  minBpm: number
  maxBpm: number
}

export const EMPTY_DANCE: Dance = {
  id: 0,
  name: '',
  minBpm: 0,
  maxBpm: 0,
}

