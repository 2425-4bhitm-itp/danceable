import { set } from 'model/model'
import { Song } from 'model/song/song'

const SONG_URL = '/api/songs'

export async function fetchAllSongsToModel() {
  const songs = await fetchAllSongs()

  set((model) => (model.songs = new Map(songs.map((s) => [s.id, s]))))
}

export async function fetchAllSongs() {
  let songs: Song[] = []

  try {
    const response = await fetch(SONG_URL)

    if (!response.ok) {
      throw new Error(
        `HTTP error while fetching songs from ${SONG_URL}! Status: ${response.status}`
      )
    }

    songs = (await response.json()) as Song[]
  } catch (error) {
    console.log(error.toString())
  }

  return songs
}

export async function patchSong(song: Song) {
  try {
    const response = await fetch(`${SONG_URL}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(song),
    })

    if (!response.ok) {
      throw new Error(
        `HTTP error while updating song with ID ${song.id}! Status: ${response.status}`
      )
    }

    return response
  } catch (error) {
    console.error(error.toString())
    throw error
  }
}

export async function deleteSong(songId: number) {
  try {
    const response = await fetch(`${SONG_URL}/${songId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(
        `HTTP error while deleting song with ID ${songId}! Status: ${response.status}`
      )
    }

    return response
  } catch (error) {
    console.error(error.toString())
    throw error
  }
}
