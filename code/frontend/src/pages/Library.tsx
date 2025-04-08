import ClipFilter from '../components/ClipFilter'
import ClipTile from '../components/ClipTile'
import { useClipsFilter } from '../stores/clips-filter/clipsFilterStore'
import { useClipStore } from '../stores/clip/clipStore'
import { useSongStore } from '../stores/song/songStore'
import EditSongModal from '../components/EditSongModal'
import SwitchSongModal from '../components/SwitchSongModal'

function Library() {
  const clips = useClipStore((state) => state.clips)
  const danceFilterIds = useClipsFilter((state) => state.danceIds)
  const { songs } = useSongStore()

  return (
    <>
      <h1 className="px-2 pt-9 pb-2 text-3xl">Library</h1>
      <EditSongModal />
      <ClipFilter />
      <SwitchSongModal />
      <div className="flex w-full flex-col items-center overflow-y-auto">
        {Array.from(clips.values())
          .filter((c) => {
            const song = songs.get(c.songId)
            return danceFilterIds.size == 0 || (song && danceFilterIds.has(song?.danceId))
          })
          .map((c) => (
            <ClipTile key={c.id} clipId={c.id} />
          ))}
      </div>
    </>
  )
}

export default Library
