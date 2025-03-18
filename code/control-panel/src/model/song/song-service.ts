import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'
import { Song } from 'model/song/song'
import { fetchAllDances } from 'model/dance/dance-service'

export async function fetchAllSongsToModel() {
  const songs = await fetchAllSongs()

  set((model) => (model.songs = songs))
}

export async function fetchAllSongs() {
  const response = await fetch('/api/songs')
  return await response.json() as Song[]
}