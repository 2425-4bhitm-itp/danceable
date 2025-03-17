import { Dance } from '../dance/dance'
import { Song } from '../song/song'

export interface Snippet {
  id: number
  song: Song
  dances: Dance[]
  songSnippetIndex: number
  speed: number
  fileName: string
}
