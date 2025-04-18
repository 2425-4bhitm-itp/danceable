import { create } from 'zustand'
import { Song } from './song'
import { OnError } from '../../utils/OnError'

const SONGS_URL = '/api/songs'

type SongStore = {
  songs: Map<number, Song>
  fetchSongs: (onError: OnError) => Promise<boolean>
  patchSong: (song: Song, onError: OnError) => Promise<boolean>
  addSong: (song: Song, onError: OnError) => Promise<boolean>
  editSongId: number | null
  setEditSongId: (id: number | null) => void
  isAddingSong: boolean
  setIsAddingSong: (isAddingSong: boolean) => void
}

export const useSongStore = create<SongStore>((set) => ({
  songs: new Map(),
  fetchSongs: async (onError) => {
    const response = await fetch(SONGS_URL)

    if (response.ok) {
      const songsArray = (await response.json()) as Song[]

      set({
        songs: new Map(songsArray.map((d) => [d.id, d])),
      })
    } else {
      onError?.('Something went wrong when fetching songs!')
    }

    return response.ok
  },
  patchSong: async (song, onError) => {
    const response = await fetch(SONGS_URL, {
      method: 'PATCH',
      body: JSON.stringify(song),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const isValid = (response.ok && song.id) as boolean

    if (isValid) {
      set((state) => {
        const updatedSongs = new Map(state.songs)
        updatedSongs.set(song.id, song)
        return { songs: updatedSongs }
      })
    } else {
      onError?.('Something went wrong when patching song!')
    }

    return isValid
  },
  addSong: async (song, onError) => {
    const response = await fetch(SONGS_URL, {
      method: 'POST',
      body: JSON.stringify(song),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const isValid = (response.ok && song.id) as boolean

    if (isValid) {
      set((state) => {
        const updatedSongs = new Map(state.songs)
        updatedSongs.set(song.id, song)
        return { songs: updatedSongs }
      })
    } else {
      onError?.('Something went wrong when adding song!')
    }

    return isValid
  },
  editSongId: null,
  setEditSongId: (id) => set({ editSongId: id }),
  isAddingSong: false,
  setIsAddingSong: (isAddingSong) => {
    set({ isAddingSong })
  },
}))
