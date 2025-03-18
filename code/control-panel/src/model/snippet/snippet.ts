import { Song, EMPTY_SONG } from 'model/song/song'

export interface Snippet {
  id: number
  song: Song
  songSnippetIndex: number
  speed: number
  fileName: string
}

export const EMPTY_SNIPPET: Snippet = {
  id: 0,
  song: EMPTY_SONG,
  songSnippetIndex: 0,
  speed: 0,
  fileName: '',
}