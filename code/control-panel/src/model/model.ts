import { apply, Subject } from 'lib/observable'

import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { Song } from 'model/song/song'
import { DanceFilter } from 'model/dance-filter/dance-filter'

import { WriteableDraft } from 'lib/immer'

interface Model {
  currentPane: string
  snippets: Snippet[]
  songs: Song[]
  dances: Dance[]
  danceFilters: DanceFilter[]
  songToEdit: number
}

const state: Model = {
  currentPane: '',
  snippets: [],
  songs: [],
  dances: [],
  danceFilters: [],
  songToEdit: -1,
}

const store = new Subject(state)

function set(recipe: (model: WriteableDraft<Model>) => void) {
  apply(store, recipe)
}

export { Model, store, set }
