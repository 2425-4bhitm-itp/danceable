import { apply, Subject } from 'lib/observable'

import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { Song } from 'model/song/song'
import { DanceFilter } from 'model/dance-filter/dance-filter'

import { libraryRoute } from 'components/library'
import { WriteableDraft } from 'lib/immer'

interface Model {
  currentPane: string
  snippets: Snippet[]
  songs: Song[]
  dances: Dance[]
  danceFilters: DanceFilter[]
}

const cachedModel: Model = null // readModelFromSessionStorage()

const state: Model = cachedModel
  ? cachedModel
  : {
      currentPane: '/' + libraryRoute,
      snippets: [],
      songs: [],
      dances: [],
      danceFilters: [],
    }

const store = new Subject(state)

function set(recipe: (model: WriteableDraft<Model>) => void) {
  apply(store, recipe)
}

export { Model, store, set }
