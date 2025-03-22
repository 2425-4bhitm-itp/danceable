import { set } from 'model/model'
import { Song } from 'model/song/song'

const SONG_URL = '/api/songs'

export async function fetchAllSongsToModel() {
  const songs = await fetchAllSongs()

  set((model) => songs)
}

export async function fetchAllSongs() {
  let songs: Song[] = []

  try {
    const response = await fetch(SONG_URL)

    if (!response.ok) {
      throw new Error(`HTTP error while fetching songs from ${SONG_URL}! Status: ${response.status}`)
    }

    songs = await response.json() as Song[]
  } catch (error) {
    console.log(error.toString())
  }

  return songs
}