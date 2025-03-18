import { Dance } from '../dance/dance'
import { Song, EMPTY_SONG } from '../song/song'

export interface Snippet {
  id: number
  song: Song
  dances: Dance[]
  songSnippetIndex: number
  speed: number
  fileName: string
}

export const EMPTY_SNIPPET: Snippet = {
  id: 0,
  song: EMPTY_SONG,
  dances: [],
  songSnippetIndex: 0,
  speed: 0,
  fileName: '',
}