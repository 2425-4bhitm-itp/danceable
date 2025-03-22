import { Observable } from 'lib/observable'

import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { Song } from 'model/song/song'
import { DanceFilter } from 'model/dance-filter/dance-filter'

import { libraryRoute } from 'components/library'
import { readModelFromSessionStorage } from 'lib/cache'

interface Model {
  currentPane: string,
  snippets: Snippet[]
  songs: Song[],
  dances: Dance[],
  danceFilters: DanceFilter[]
}

const cachedModel: Model = readModelFromSessionStorage()

const state: Model = cachedModel ? cachedModel : {
  currentPane: '/' + libraryRoute,
  snippets: [],
  songs: [],
  dances: [],
  danceFilters: [],
}

const store = new Observable(state)

function set(recipe: (model: Model) => void) {
  recipe(store.value)
}

function subscribe(observer: (model: Model) => void) {
  store.subscribe(observer)
}

export { Model, subscribe, set }
