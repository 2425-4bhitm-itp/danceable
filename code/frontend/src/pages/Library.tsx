import ClipFilter from '../components/ClipFilter'
import ClipTile from '../components/ClipTile'
import { useClipsFilter } from '../stores/clips-filter/clipsFilterStore'
import { useClipStore } from '../stores/clip/clipStore'
import { useSongStore } from '../stores/song/songStore'
import AddSongModal from '../components/modals/AddSongModel'
import EditSongModal from '../components/modals/EditSongModal'
import SwitchSongModal from '../components/modals/SwitchSongModal'
import AddClipModal from '../components/modals/AddClipModal'
import { useDanceStore } from '../stores/dance/danceStore'
import { useToastStore } from '../stores/toast/toastStore'
import { ToastType } from '../components/toast/ToastType'
import { ToastData } from '../stores/toast/ToastData'
import { useEffect } from 'react'

import uploadIcon from '../assets/icons/upload.svg'

function Library() {
  const { clips, fetchClips, setIsAddingClip } = useClipStore()
  const danceFilterIds = useClipsFilter((state) => state.danceIds)
  const { songs, setIsAddingSong, fetchSongs } = useSongStore()
  const { fetchDances } = useDanceStore()
  const { createToast } = useToastStore()

  useEffect(() => {
    const fetchData = async () => {
      await fetchClips((message) =>
        createToast({
          type: ToastType.ERROR,
          message: message,
          timeToLive: 3000,
        } as ToastData)
      )

      await fetchSongs((message) =>
        createToast({
          type: ToastType.ERROR,
          message: message,
          timeToLive: 3000,
        } as ToastData)
      )

      await fetchDances((message) =>
        createToast({
          type: ToastType.ERROR,
          message: message,
          timeToLive: 3000,
        } as ToastData)
      )
    }

    fetchData()
  }, [])

  return (
    <>
      <EditSongModal />
      <SwitchSongModal />
      <AddClipModal />
      <AddSongModal />
      <h1 className="px-2 pt-8 text-3xl">Library</h1>
      <div className="flex flex-row-reverse gap-1 px-4">
        <button
          className="bg-gray-dark flex cursor-pointer gap-2 rounded-xl px-5 py-1 font-medium text-white"
          onClick={() => setIsAddingClip(true)}
        >
          <img className="w-5" src={uploadIcon} alt="upload icon" />
          upload clips
        </button>
        <button
          className="border-gray-dark cursor-pointer rounded-xl border-2 bg-white px-4 py-0.5 font-medium"
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
