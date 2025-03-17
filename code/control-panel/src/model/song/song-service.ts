import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'
import { Song } from 'model/song/song'

export async function fetchAllSongs() {
  const response = await fetch('/api/songs')
  const songs = await response.json() as Song[]

  set((model) => (model.songs = songs))
}
