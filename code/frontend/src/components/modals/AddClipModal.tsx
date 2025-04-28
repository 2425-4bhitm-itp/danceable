import { useEffect, useRef, useState } from 'react'
import { useToastStore } from '../../stores/toast/toastStore'
import { ToastType } from '../toast/ToastType'
import { ToastData } from '../../stores/toast/ToastData'
import { useClipStore } from '../../stores/clip/clipStore'
import { useSongStore } from '../../stores/song/songStore'

function AddClipModal() {
  const { addClip, isAddingClip, setIsAddingClip } = useClipStore()
  const { createToast } = useToastStore()
  const [songId, setSongId] = useState<number | null>(null)
  const { songs } = useSongStore()

  const [isDragging, setIsDragging] = useState<boolean>(false)
  const [clipFiles, setClipFiles] = useState<File[]>([])
  const dialogRef = useRef<HTMLDialogElement | null>(null)
  const dragDropRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (isAddingClip && !dialog.open) {
      dialog.showModal()
    } else if (!isAddingClip && dialog.open) {
      dialog.close()
    }
  }, [isAddingClip])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (songId && clipFiles.length > 0) {
      clipFiles.forEach((clipFile) => addClip(clipFile))
    }

    close()
  }

  const close = () => {
    dialogRef.current?.close()
    setIsAddingClip(false)
  }

  useEffect(() => console.log(clipFiles), [clipFiles])

  function inputClipFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const fileInput: FileList | null = event.target.files

    if (!fileInput) return

    setClipFilesIfWav(Array.from(fileInput))
  }

  function handleDrop(event: React.DragEvent<HTMLElement>) {
    event.preventDefault()

    const files: File[] = []

    if (event.dataTransfer?.items) {
      Array.from(event.dataTransfer.items).forEach((item) => {
        if (item.kind === 'file') {
          const file = item.getAsFile()
          if (file) files.push(file)
        }
      })
    }

    setClipFilesIfWav(files)
    setIsDragging(false)
  }

  function setClipFilesIfWav(allFiles: File[]) {
    const waveFiles: File[] = allFiles.filter((file: File) => file.type === 'audio/wav')

    if (waveFiles.length > 0) {
      setClipFiles(waveFiles)
      console.log(waveFiles)
    } else {
      createToast({
        type: ToastType.ERROR,
        message: 'Only .wav files are allowed!',
        timeToLive: 1000,
      } as ToastData)
    }
  }

  function handleDragOver(event: React.DragEvent<HTMLElement>) {
    event.preventDefault()
    console.log('drag over')
  }

  function handleDragEnter(event: React.DragEvent<HTMLElement>) {
    event.preventDefault()
    setIsDragging(true)
    console.log('drag over target')
  }

  function handleDragLeave(event: React.DragEvent<HTMLElement>) {
    event.preventDefault()

    console.log('drag leave')

    setIsDragging(false)
  }

  return (
    <dialog
      ref={dialogRef}
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transform rounded-xl border-2 border-gray-200 p-9"
    >
      <h2 className="mb-3 text-2xl">Add Clips</h2>

      <form className="flex min-w-80 flex-col gap-3" onSubmit={handleSubmit}>
        <label className="flex flex-col">
          Pick a song to upload clips for:
          <select
            name="song"
            value={songId ?? ''}
            onChange={(e) => setSongId(Number(e.target.value))}
            className="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
          >
            <option value="" disabled>
              Select a song
            </option>

            {Array.from(songs.values()).map((song) => (
              <option key={song.id} value={song.id}>
                {song.title}
              </option>
            ))}
          </select>
        </label>

        <div
          className={`relative box-border flex w-full items-center justify-center rounded-lg border-2 border-dashed border-gray-200 p-16`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          ref={dragDropRef}
        >
          <div
            className={`pointer-events-none absolute top-0 left-0 z-10 h-full w-full rounded-lg bg-gray-300 transition-all ${
              isDragging ? 'opacity-20' : 'opacity-0'
            }`}
          >
            <div className="flex h-full w-full flex-col-reverse items-center p-1">
              Only .wav files are accepted!
            </div>
          </div>
          <div className="text-center">
            <label
              htmlFor="file-upload"
              className="py- inline-block cursor-pointer rounded-lg border-2 border-gray-200 px-5 py-1 transition duration-200"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
            >
              Choose Files
            </label>
            <input
              onChange={inputClipFiles}
              id="file-upload"
              type="file"
              className="hidden"
              multiple
            />
          </div>
        </div>

        <div className="flex justify-center gap-2 pt-2">
          <button
            className="cursor-pointer rounded-lg bg-gray-100 px-5 py-1 hover:bg-gray-200"
            onClick={close}
          >
            cancel
          </button>
          <button
            type="submit"
            className="bg-gray-dark cursor-pointer rounded-lg px-5 py-1 text-white select-none hover:text-white"
            disabled={!songId || !clipFiles}
          >
            upload
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default AddClipModal
