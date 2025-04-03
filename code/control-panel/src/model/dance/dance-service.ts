import { set } from 'model/model'
import { Dance } from 'model/dance/dance'
import { DanceFilter } from 'model/dance-filter/dance-filter'

const DANCES_URL = '/api/dances'

export async function fetchAllDancesToModel() {
  const dances = await fetchAllDances()

  set((model) => {
    model.dances = new Map(dances.map((d) => [d.id, d]))

    const danceFilters = Array.from(
      dances.map((d, i) => {
        return {
          danceId: d.id,
          isEnabled:
            model.danceFilters.length >= i && model.danceFilters[i]
              ? model.danceFilters[i].isEnabled
              : false,
        } as DanceFilter
      })
    )

    model.danceFilters = danceFilters
  })
}

export async function fetchAllDances() {
  let dances: Dance[] = []

  try {
    const response = await fetch(DANCES_URL)

    if (!response.ok) {
      throw new Error(
        `HTTP error while fetching dances from ${DANCES_URL}! Status: ${response.status}`
      )
    }

    dances = (await response.json()) as Dance[]
  } catch (error) {
    console.log(error.toString())
  }

  return dances
}
