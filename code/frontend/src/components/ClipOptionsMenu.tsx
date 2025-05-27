import { useEffect, useRef, useState } from 'react'
import optionsIcon from '../assets/icons/options-icon-dark.svg'
import { useSongStore } from '../stores/song/songStore'
import { useClipStore } from '../stores/clip/clipStore'

interface ClipOptionsMenuProps {
  clipId: number
}

function ClipOptionsMenu(props: ClipOptionsMenuProps) {


  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
          popoverRef.current &&
          triggerRef.current &&
          !popoverRef.current.contains(event.target as Node) &&
          !triggerRef.current.contains(event.target as Node)
      ) {
        close()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])
  const popoverRef = useRef<HTMLDivElement | null>(null)
  const triggerRef = useRef<HTMLButtonElement | null>(null)

  const [isVisible, setIsVisible] = useState(false)
  const { setEditSongId } = useSongStore()
  const { setSwitchSongClipId, deleteClip } = useClipStore()
  const clip = useClipStore((state) => state.clips.get(props.clipId))

  if (!clip || !clip.songId) {
    return null
  }

  const toggleVisibility = () => {
    setIsVisible(!isVisible)
  }

  const close = () => {
    setIsVisible(false)
  }

  return (
    <div className="relative w-8">
      <button
        ref={triggerRef}
        onClick={toggleVisibility}
        className="clip-options-button flex aspect-square w-full items-center justify-center rounded-md hover:bg-gray-100"
      >
        <img className="w-full" src={optionsIcon} alt="options button" />
      </button>

      {isVisible && (
        <div
          ref={popoverRef}
          className="clip-options absolute top-0 right-8 flex min-w-12 flex-col rounded-md bg-white p-1 text-nowrap shadow"
        >
          <button className="analyse-song-option rounded px-2 py-1 text-left text-purple-500 hover:bg-gray-100">
            analyse
          </button>
          <button
            className="switch-song-option rounded px-2 py-1 text-left hover:bg-gray-100"
            onClick={() => {
              setSwitchSongClipId(clip.id)
              close()
            }}
          >
            switch song
          </button>
          <button
            className="edit-song-option rounded px-2 py-1 text-left hover:bg-gray-100"
            onClick={() => {
              setEditSongId(clip.songId)
              close()
            }}
          >
            edit song
          </button>
          <button
            className="delete-song-option rounded px-2 py-1 text-left text-red-400 hover:bg-gray-100"
            onClick={() => deleteClip(clip.id, (message) => console.log(message))}
          >
            delete clip
          </button>
        </div>
      )}
    </div>
  )
}

export default ClipOptionsMenu
