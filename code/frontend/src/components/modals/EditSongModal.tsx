import { useState, useRef, useEffect } from 'react'
import { useDanceStore } from '../../stores/dance/danceStore'
import { Song } from '../../stores/song/song'
import { useSongStore } from '../../stores/song/songStore'
import { useToastStore } from '../../stores/toast/toastStore'
import { ToastType } from '../toast/ToastType'
import { ToastData } from '../../stores/toast/ToastData'

function EditSongModal() {
  const { songs, patchSong, editSongId, setEditSongId } = useSongStore()
  const { dances } = useDanceStore()
  const { createToast } = useToastStore()

  const song = songs.get(editSongId ?? -1)

  const [title, setTitle] = useState('')
  const [speed, setSpeed] = useState(-1)
  const [danceId, setDanceId] = useState<number | null>(null)

  const dialogRef = useRef<HTMLDialogElement | null>(null)

  useEffect(() => {
    if (song) {
      setTitle(song.title)
      setSpeed(song.speed)
      setDanceId(song.danceId)
    }
  }, [song])

  useEffect(() => {
    dialogRef.current?.addEventListener('click', (e) => {
      if (e.target === dialogRef.current) {
        dialogRef.current?.close()
      }
    })
  }, [dialogRef])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!title || danceId === null) {
      return
    }

    const updatedSong: Song = {
      id: song?.id ?? -1,
      title,
      speed,
      danceId,
    }

    patchSong(updatedSong, (message) =>
      createToast({
        type: ToastType.ERROR,
        message: message,
        timeToLive: 3000,
      } as ToastData)
    )
    close()
  }

  const close = () => {
    setEditSongId(null)
  }

  useEffect(() => {
    if (editSongId) {
      dialogRef.current?.showModal()
    }
  }, [editSongId])

  if (!editSongId || !song) {
    return null
  }

  return (
    <dialog
      id="editDanceModal"
      ref={dialogRef}
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transform rounded-xl border-2 border-gray-200 p-9"
    >
      <h2 className="mb-3 text-2xl">Edit Song</h2>
      <form className="flex min-w-80 flex-col gap-3" onSubmit={handleSubmit}>
        <label className="flex flex-col">
          <span>Title:</span>
          <input
            required
            name="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
          />
        </label>

        <label className="flex flex-col">
          <span>Speed:</span>
          <input
            required
            name="speed"
            type="number"
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
          />
        </label>

        <label className="flex flex-col">
          <span>Dance:</span>
          <select
            name="dance"
            value={danceId ?? ''}
            onChange={(e) => setDanceId(Number(e.target.value))}
            className="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
          >
            <option value="" disabled>
              Select a dance
            </option>
            {Array.from(dances.values()).map((dance) => (
              <option key={dance.id} value={dance.id}>
                {dance.name}
              </option>
            ))}
          </select>
        </label>

        <div className="flex justify-center gap-2 pt-2">
          <button
            className="cursor-pointer rounded-lg bg-gray-100 px-5 py-1 hover:bg-gray-200"
            onClick={close}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="bg-gray-dark cursor-pointer rounded-lg px-5 py-1 text-white hover:text-white"
          >
            save
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default EditSongModal
