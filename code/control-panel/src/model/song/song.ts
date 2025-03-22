import { Dance } from 'model/dance/dance'

export interface Song {
  readonly id: number
  readonly title: string
  readonly dances: Dance[]
}