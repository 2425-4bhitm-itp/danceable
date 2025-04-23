import ClipFilter from '../components/ClipFilter'
import ClipTile from '../components/ClipTile'
import { useClipsFilter } from '../stores/clips-filter/clipsFilterStore'
import { useClipStore } from '../stores/clip/clipStore'
import { useSongStore } from '../stores/song/songStore'
import AddSongModal from '../components/modals/AddSongModel'
import EditSongModal from '../components/modals/EditSongModal'
import SwitchSongModal from '../components/modals/SwitchSongModal'

function Library() {
  const clips = useClipStore((state) => state.clips)
  const danceFilterIds = useClipsFilter((state) => state.danceIds)
  const { songs, setIsAddingSong } = useSongStore()

  return (
    <>
      <EditSongModal />
      <SwitchSongModal />
      <AddSongModal />
      <h1 className="px-2 pt-8 text-3xl">Library</h1>
      <div className="flex flex-row-reverse px-4">
        <button
          id="uploadSnippetButton"
          className="bg-gray-dark cursor-pointer rounded-xl px-5 py-1 font-medium text-white"
          onClick={() => setIsAddingSong(true)}
        >
          add song
        </button>
      </div>
      <ClipFilter />
      <div className="flex w-full flex-col items-center overflow-y-auto">
        {Array.from(clips.values())
          .filter((c) => {
            const song = songs.get(c.songId)
            return danceFilterIds.size == 0 || (song && danceFilterIds.has(song?.danceId))
          })
          .sort((a, b) => {
            const titleA = songs.get(a.songId)?.title ?? ''
            const titleB = songs.get(b.songId)?.title ?? ''

            const comparedByTitle = titleA.localeCompare(titleB)

            return comparedByTitle == 0 ? Math.sign(a.id - b.id) : comparedByTitle
          })
          .map((c) => (
            <ClipTile key={c.id} clipId={c.id} />
          ))}
      </div>
    </>
  )
}

export default Library
