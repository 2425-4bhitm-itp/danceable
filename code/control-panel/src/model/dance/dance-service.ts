import { set } from 'model/model'
import { Dance } from 'model/dance/dance'
import { DanceFilter } from 'model/dance-filter/dance-filter'

export async function fetchAllDancesToModel() {
  const dances = await fetchAllDances()

  set((model) => {
    model.dances = dances

    model.danceFilters = dances.map(d => {
      const previousDanceFilter = model.danceFilters.find(mD => mD.dance.id === d.id)

      return {
        dance: d,
        isEnabled: previousDanceFilter == undefined ? false : previousDanceFilter.isEnabled,
      } as DanceFilter
    })
  })
}

export async function fetchAllDances() {
  const response = await fetch('/api/dances')
  return await response.json() as Dance[]
}
