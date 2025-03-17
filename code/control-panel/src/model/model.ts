import { Observable } from 'lib/observable'
import { libraryRoute } from 'components/library'

interface Model {
  currentPane: string
}

const state: Model = {
  currentPane: '/' + libraryRoute,
}

const store = new Observable(state)

function set(recipe: (model: Model) => void) {
  recipe(store.value)
}

function subscribe(observer: (model: Model) => void) {
  store.subscribe(observer)
}

export { Model, subscribe, set }
