import { create } from 'zustand'
import { Song } from './song'

const SONGS_URL = '/api/songs'

type SongStore = {
  songs: Map<number, Song>
  fetchSongs: () => Promise<void>
  patchSong: (song: Song) => Promise<void>
  editSongId: number | null
  setEditSongId: (id: number | null) => void
}

export const useSongStore = create<SongStore>((set, get) => ({
  songs: new Map(),
  fetchSongs: async () => {
    const response = await fetch(SONGS_URL)

    const songsArray = (await response.json()) as Song[]

    set({ songs: new Map(songsArray.map((d) => [d.id, d])) })
  },
  patchSong: async (song) => {
    const oldSong = (await get().songs).get(song.id)

    if (oldSong) {
      set((state) => {
        const updatedSongs = new Map(state.songs)
        updatedSongs.set(song.id, song)
        return { songs: updatedSongs }
      })

      const response = await fetch(SONGS_URL, {
        method: 'PATCH',
        body: JSON.stringify(song),
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        set((state) => {
          const updatedSongs = new Map(state.songs)
          updatedSongs.set(oldSong.id, oldSong)
          return { songs: updatedSongs }
        })
      }
    }
  },
  editSongId: null,
  setEditSongId: (id) => set({ editSongId: id }),
}))
