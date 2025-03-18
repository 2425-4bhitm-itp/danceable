import { Dance } from 'model/dance/dance'

export interface Song {
  id: number
  title: string
  dances: Dance[]
}

export const EMPTY_SONG: Song = {
  id: 0,
  title: '',
  dances: []
}
