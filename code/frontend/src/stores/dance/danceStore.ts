import { create } from 'zustand'
import { Dance } from './dance'

type DanceStore = {
  dances: Map<number, Dance>
  fetchDances: () => Promise<void>
}

export const useDanceStore = create<DanceStore>((set) => ({
  dances: new Map(),
  fetchDances: async () => {
    const response = await fetch('/api/dances')

    const dancesArray = (await response.json()) as Dance[]
    console.log(dancesArray)

    set({ dances: new Map(dancesArray.map((d) => [d.id, d])) })
  },
}))
