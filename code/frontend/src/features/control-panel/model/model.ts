import { Observable } from "../../../lib/observable"

interface Model {
  currentPane: string
}

const state: Model = {
  currentPane: "/todos",
}

const store = new Observable(state)

function set(recipe: (model: Model) => void) {
  recipe(store.value)
}

function subscribe(observer: (model: Model) => void) {
  store.subscribe(observer)
}

export { Model, subscribe, set }