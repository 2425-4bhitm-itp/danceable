import { useEffect, useRef, useState } from 'react'
import { Clip } from '../../stores/clip/clip'
import { Song } from '../../stores/song/song'
import { useClipStore } from '../../stores/clip/clipStore'
import { useSongStore } from '../../stores/song/songStore'
import { useToastStore } from '../../stores/toast/toastStore'
import { ToastType } from '../toast/ToastType'
import { ToastData } from '../../stores/toast/ToastData'

function SwitchSongModal() {
  const { songs } = useSongStore()
  const { clips, switchSongClipId, setSwitchSongClipId, updateClip: patchClip } = useClipStore()
  const { createToast } = useToastStore()

  const clip = clips.get(switchSongClipId ?? -1)

  const [songId, setSongId] = useState(-1)

  const dialogRef = useRef<HTMLDialogElement | null>(null)

  useEffect(() => {
    if (clip) {
      setSongId(clip.songId)
    }
  }, [clip])

  useEffect(() => {
    dialogRef.current?.addEventListener('click', (e) => {
      if (e.target === dialogRef.current) {
        dialogRef.current?.close()
      }
    })
  }, [dialogRef])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (songId === null) {
      return
    }

    const updatedClip: Clip = {
      id: clip?.id ?? -1,
      songId,
      fileName: '',
    }

    console.log('song id', songId)

    patchClip(updatedClip, (message) =>
      createToast({
        type: ToastType.ERROR,
        message: message,
        timeToLive: 3000,
      } as ToastData)
    )
    close()
    close()
  }

  const close = () => {
    setSwitchSongClipId(null)
  }

  useEffect(() => {
    if (switchSongClipId) {
      dialogRef.current?.showModal()
    }
  }, [switchSongClipId])

  if (!switchSongClipId || !clip) {
    return null
  }

  return (
    <dialog
      id="editDanceModal"
      ref={dialogRef}
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transform rounded-xl border-2 border-gray-200 p-9"
    >
      <h2 className="text-2xl">Switch Song for clip ({clip.id})</h2>
      <form className="flex max-w-fit flex-col items-center gap-1 py-3" onSubmit={handleSubmit}>
        <label htmlFor="song" className="flex w-full items-center justify-between gap-2">
          <span>Song:</span>
          <select
            className="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
            name="song"
            value={songId ?? ''}
            onChange={(e) => setSongId(Number(e.target.value))}
          >
            {Array.from(songs.values()).map((s: Song) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
        </label>
        <div className="flex justify-center gap-2">
          <button
            className="cursor-pointer rounded-lg bg-gray-100 px-5 py-1 select-none hover:bg-gray-200"
            onClick={close}
          >
            cancel
          </button>
          <button
            type="submit"
            className="bg-gray-dark cursor-pointer rounded-lg px-5 py-1 text-white select-none hover:text-white"
          >
            save
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default SwitchSongModal
