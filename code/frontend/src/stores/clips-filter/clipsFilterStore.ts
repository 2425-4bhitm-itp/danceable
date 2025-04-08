import { create } from "zustand"

type ClipsFilterStore = {
  danceIds: Set<number>
  toggleDanceId: (id: number) => void
}

export const useClipsFilter = create<ClipsFilterStore>((set) => ({
  danceIds: new Set,
  toggleDanceId: (id: number) => set(state => {
    const newDanceIds = new Set(state.danceIds);

    if (state.danceIds.has(id)) {
      newDanceIds.delete(id);
    } else {
      newDanceIds.add(id);
    }

    return { danceIds: newDanceIds }
  })
}))
