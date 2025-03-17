import { Observable } from 'lib/observable'

import { Snippet } from './snippet/snippet'
import { Dance } from './dance/dance'

import { libraryRoute } from 'components/library'

interface Model {
  currentPane: string,
  snippets: Snippet[],
  dances: Dance[]
}

const state: Model = {
  currentPane: '/' + libraryRoute,
  snippets: [],
  dances: []
}

const store = new Observable(state)

function set(recipe: (model: Model) => void) {
  recipe(store.value)
}

function subscribe(observer: (model: Model) => void) {
  store.subscribe(observer)
}

export { Model, subscribe, set }
