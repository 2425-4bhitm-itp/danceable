import { Model, set } from 'model/model'

export function updateModelFromSessionStorage() {
  set(model => {
    const cachedModel = readModelFromSessionStorage()
    if (cachedModel) {
      model = cachedModel
      console.log('read from session: ' + cachedModel.currentPane)
    }
  })
}

export function saveModelToSessionStorage(model: Model) {
  console.log('write to session: ' + model.currentPane)
  sessionStorage.setItem('model', JSON.stringify(model))
}

export function readModelFromSessionStorage(): Model {
  const rawModel = sessionStorage.getItem('model')
  let model: Model | null = null

  if (rawModel) {
    model = JSON.parse(rawModel)
  }

  return model
}