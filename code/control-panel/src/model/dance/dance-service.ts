import { set } from 'model/model'
import { Dance } from 'model/dance/dance'

export async function fetchAllDances() {
  const response = await fetch('/api/dances')
  const dances = await response.json() as Dance[]

  set((model) => (model.dances = dances))
}
