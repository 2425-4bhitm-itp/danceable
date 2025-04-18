import { create } from 'zustand'
import { Dance } from './dance'
import { OnError } from '../../utils/OnError'

type DanceStore = {
  dances: Map<number, Dance>
  fetchDances: (onError: OnError) => Promise<boolean>
}

export const useDanceStore = create<DanceStore>((set) => ({
  dances: new Map(),
  fetchDances: async (onError) => {
    const response = await fetch('/api/dances')

    if (response.ok) {
      const dancesArray = (await response.json()) as Dance[]
      set({ dances: new Map(dancesArray.map((d) => [d.id, d])) })
    } else {
      onError?.('Something went wrong when fetching dances!')
    }

    return response.ok
  },
}))
