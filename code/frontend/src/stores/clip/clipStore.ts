import { create } from 'zustand'
import { Clip } from './clip'
import { OnError } from '../../utils/OnError'

const CLIPS_URL = '/api/clips'

type ClipStore = {
  clips: Map<number, Clip>
  switchSongClipId: number | null
  setSwitchSongClipId: (id: number | null) => void
  fetchClips: (onError: OnError) => Promise<boolean>
  addClip: (clip: Clip, onError: OnError) => Promise<boolean>
  updateClip: (clip: Clip, onError: OnError) => Promise<boolean>
  deleteClip: (id: number, onError: OnError) => Promise<boolean>
  uploadAddClips: (clipFiles: File[], onError: OnError) => Promise<boolean>
  isAddingClip: boolean
  setIsAddingClip: (isAddingClip: boolean) => void
  uploadClipFiles: (clipFiles: File[], onError: OnError) => Promise<boolean>
}

export const useClipStore = create<ClipStore>((set) => ({
  clips: new Map(),
  switchSongClipId: null,
  setSwitchSongClipId: (id) => set({ switchSongClipId: id }),
  fetchClips: async (onError) => {
    const response = await fetch('/api/clips')

    if (response.ok) {
      const clipsArray = (await response.json()) as Clip[]

      set({ clips: new Map(clipsArray.map((d) => [d.id, d])) })
    } else {
      onError?.('Something went wrong when fetching clips!')
    }

    return response.ok
  },
  addClip: async (clip, onError) => {
    const response = await fetch(CLIPS_URL, {
      method: 'POST',
      body: JSON.stringify(clip),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      set((state) => {
        const updatedClips = new Map(state.clips)
        updatedClips.set(clip.id, clip)
        return { clips: updatedClips }
      })
    } else {
      onError?.('Something went wrong when creating clip!')
    }

    return response.ok
  },
  updateClip: async (clip, onError) => {
    const response = await fetch(CLIPS_URL, {
      method: 'PATCH',
      body: JSON.stringify(clip),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      set((state) => {
        const updatedClips = new Map(state.clips)
        updatedClips.set(clip.id, clip)
        return { clips: updatedClips }
      })
    } else {
      onError?.('Something went wrong when updating clip!')
    }

    return response.ok
  },
  deleteClip: async (id, onError) => {
    const response = await fetch(CLIPS_URL + '/' + id, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      set((state) => {
        const newClips = new Map(state.clips)
        newClips.delete(id)
        return { clips: newClips }
      })
    } else {
      onError?.('Something went wrong when deleting clip!')
    }

    return response.ok
  },
  uploadAddClips: async (clipFiles, onError) => {
    return true
  },
  isAddingClip: false,
  setIsAddingClip: (isAddingClip) => {
    set({ isAddingClip: isAddingClip })
  },
  uploadClipFiles: async (clipFiles, onError) => {
    // TODO: implement sending to server and adding clips
    return true
  },
}))
