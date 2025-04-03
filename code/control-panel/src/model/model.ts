import { apply, Subject } from 'lib/observable'

import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { Song } from 'model/song/song'
import { DanceFilter } from 'model/dance-filter/dance-filter'

import { WriteableDraft } from 'lib/immer'

interface Model {
  currentPane: string
  snippets: Snippet[]
  songs: Map<number, Song>
  dances: Map<number, Dance>
  danceFilters: DanceFilter[]
  songToEdit: number
  snippetToSwitchSong: number
}

const state: Model = {
  currentPane: '',
  snippets: [],
  songs: new Map<number, Song>(),
  dances: new Map<number, Dance>(),
  danceFilters: [],
  songToEdit: -1,
  snippetToSwitchSong: -1,
}

const store = new Subject(state)

function set(recipe: (model: WriteableDraft<Model>) => void) {
  apply(store, recipe)
}

export { Model, store, set }
