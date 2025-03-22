import { Song } from 'model/song/song'

export interface Snippet {
  readonly id: number
  readonly song: Song
  readonly songSnippetIndex: number
  readonly speed: number
  readonly fileName: string
}