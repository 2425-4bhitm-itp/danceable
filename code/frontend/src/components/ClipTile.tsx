import { Clip } from '../stores/clip/clip'
import { useClipStore } from '../stores/clip/clipStore'
import { Dance } from '../stores/dance/dance'
import { useDanceStore } from '../stores/dance/danceStore'
import { useSongStore } from '../stores/song/songStore'
import { Song } from '../stores/song/song'
import ClipOptionsMenu from './ClipOptionsMenu'

interface ClipTileProps {
  clipId: number
}

function ClipTile(props: ClipTileProps) {
  const clip: Clip | undefined = useClipStore((state) => state.clips.get(props.clipId))
  const song: Song | undefined = useSongStore((state) => state.songs.get(clip ? clip?.songId : -1))
  const dance: Dance | undefined = useDanceStore((state) =>
    state.dances.get(song ? song.danceId : -1)
  )

  if (clip && song && dance) {
    return (
      <div className="flex w-full items-center gap-5 border-t-2 border-t-gray-100 px-4 py-1.5 select-none">
        <span>
          {song.title} ({clip.id})
        </span>
        <span className="text-gray-400"> {song.speed} bpm </span>
        <div className="flex flex-1 flex-row-reverse gap-2">
          <span className="rounded-full bg-gray-100 p-0.5 px-3">{dance.name}</span>
        </div>
        <ClipOptionsMenu clipId={clip.id} />
      </div>
    )
  }

  return null
}

export default ClipTile
