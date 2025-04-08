import { create } from 'zustand'
import { Clip } from './clip'

const CLIPS_URL = '/api/clips'

type ClipStore = {
  clips: Map<number, Clip>
  fetchClips: () => Promise<void>
  patchClip: (clip: Clip) => Promise<void>
  switchSongClipId: number | null
  setSwitchSongClipId: (id: number | null) => void
}

export const useClipStore = create<ClipStore>((set, get) => ({
  clips: new Map(),
  fetchClips: async () => {
    const response = await fetch('/api/clips')

    const clipsArray = (await response.json()) as Clip[]

    console.log(clipsArray)

    set({ clips: new Map(clipsArray.map((d) => [d.id, d])) })
  },
  patchClip: async (clip) => {
    const oldClip = (await get().clips).get(clip.id)

    console.log('old clip', oldClip)
    console.log('new clip', clip)

    if (oldClip) {
      set((state) => {
        const updatedClips = new Map(state.clips)
        updatedClips.set(clip.id, clip)
        return { clips: updatedClips }
      })

      const response = await fetch(CLIPS_URL, {
        method: 'PATCH',
        body: JSON.stringify(clip),
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        set((state) => {
          const updatedClips = new Map(state.clips)
          updatedClips.set(oldClip.id, oldClip)
          return { clips: updatedClips }
        })
      }
    }
  },
  switchSongClipId: null,
  setSwitchSongClipId: (id) => set({ switchSongClipId: id }),
}))
