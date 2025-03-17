import { Observable } from 'lib/observable'

import { Snippet } from './snippet/snippet'
import { Dance } from './dance/dance'
import { Song } from 'model/song/song'

import { libraryRoute } from 'components/library'

interface Model {
  currentPane: string,
  snippets: Snippet[],
  dances: Dance[],
  songs: Song[]
}

const state: Model = {
  currentPane: '/' + libraryRoute,
  snippets: [],
  dances: [],
  songs: []
}

const store = new Observable(state)

function set(recipe: (model: Model) => void) {
  recipe(store.value)
}

function subscribe(observer: (model: Model) => void) {
  store.subscribe(observer)
}

export { Model, subscribe, set }
