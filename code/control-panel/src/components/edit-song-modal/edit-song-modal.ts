import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { Dance } from 'model/dance/dance'
import { set, store } from 'model/model'
import { Song } from 'model/song/song'
import { produce } from 'lib/immer'
import { patchSong } from 'model/song/song-service'

export const EditSongModal = 'edit-song-modal'

export class EditSongElement extends HTMLElement {
  song: Song

  connectedCallback() {
    store.subscribe((model) => {
      this.song = model.songs.find((s) => s.id === model.songToEdit)

      this.render(model.dances)
    })
  }

  render(allDances: Dance[]) {
    if (this.song) {
      const dance = allDances.find((d) => d.id === this.song.danceId)

      console.log('song', this.song)

      render(
        html` <dialog
          id="editDanceModal"
          class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transform rounded-xl border-2 border-gray-200 p-9"
        >
          <h2 class="text-2xl">Edit Song</h2>
          <form class="flex max-w-fit flex-col items-center gap-1 py-3">
            <label for="title" class="flex w-full items-center justify-between gap-2">
              <span>Title:</span>
              <input
                class="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
                name="title"
                type="text"
                value="${this.song.title}"
              />
            </label>

            <label for="speed" class="flex w-full items-center justify-between gap-2">
              <span>Speed:</span>
              <input
                class="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
                name="speed"
                type="number"
                value="${this.song.speed}"
              />
            </label>

            <label for="dance" class="flex w-full items-center justify-between gap-2">
              <span>Dance:</span>
              <select
                class="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
                name="dance"
                type="number"
              >
                ${allDances
                  .map((d) => {
                    return `<option ${this.song.danceId === d.id ? 'selected' : ''} value="${d.id}">${d.name}</option>`
                  })
                  .join('')}
              </select>
            </label>
          </form>

          <div class="flex justify-center gap-2">
            <button
              id="cancelEditDanceModal"
              class="cursor-pointer rounded-lg bg-gray-100 px-5 py-1 hover:bg-gray-200"
            >
              cancel
            </button>
            <button
              type="submit"
              id="saveEditDanceModal"
              class="bg-gray-dark cursor-pointer rounded-lg px-5 py-1 text-white hover:text-white"
            >
              save
            </button>
          </div>
        </dialog>`,
        this
      )

      document
        .querySelector('#cancelEditDanceModal')
        ?.addEventListener('click', (e) => this.close())
      document
        .querySelector('#saveEditDanceModal')
        ?.addEventListener('click', (e) => this.updateDance())

      addLinks(this)
    }
  }

  updateDance() {
    const title = (document.querySelector('input[name="title"]') as HTMLInputElement)?.value
    const speed = Number.parseInt(
      (document.querySelector('input[name="speed"]') as HTMLInputElement)?.value
    )
    const danceId = Number.parseInt(
      (document.querySelector('select[name="dance"]') as HTMLSelectElement)?.value
    )

    console.log(title, speed, danceId)

    set((model) => {
      model.songs = model.songs.map((s) => {
        if (s.id === this.song.id) {
          const song = produce(s, (draft) => {
            draft.title = title
            draft.speed = speed
            draft.danceId = danceId
          })

          patchSong(song)

          return song
        }

        return s
      })
    })
  }

  close() {
    const dialog = this.querySelector('dialog')
    if (dialog) {
      dialog.close()
    }
  }

  show() {
    const dialog = this.querySelector('dialog')
    if (dialog) {
      dialog.showModal()
    }
  }
}

customElements.define(EditSongModal, EditSongElement)
