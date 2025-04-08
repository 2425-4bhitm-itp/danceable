import { useClipsFilter } from '../stores/clips-filter/clipsFilterStore'
import { useDanceStore } from '../stores/dance/danceStore'

function ClipFilter() {
  const filterDanceIds = useClipsFilter((state) => state.danceIds)
  const dances = useDanceStore((state) => state.dances)
  const toggleDanceId = useClipsFilter((state) => state.toggleDanceId)

  return (
    <div id="dance-filters" className="flex flex-wrap gap-2 p-2">
      {Array.from(dances.values()).map((d) => (
        <button
          key={d.id}
          onClick={() => toggleDanceId(d.id)}
          className={`cursor-pointer rounded-full px-3 py-0.5 select-none ${
            filterDanceIds.has(d.id) ? 'bg-gray-300' : 'bg-gray-100'
          }`}
        >
          {d.name}
        </button>
      ))}
    </div>
  )
}

export default ClipFilter
