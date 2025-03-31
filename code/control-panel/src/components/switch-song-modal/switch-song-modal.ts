import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { set, store } from 'model/model'
import { Song } from 'model/song/song'
import { produce } from 'lib/immer'
import { Snippet } from 'model/snippet/snippet'

export const SwitchSongModal = 'switch-song-modal'

export class SwitchSongElement extends HTMLElement {
  snippet: Snippet

  constructor(state: Snippet) {
    super()
  }

  connectedCallback() {
    store.subscribe((model) => {
      this.snippet = model.snippets.find((s) => s.id === model.snippetToSwitchSong)

      this.render(model.songs)
    })
  }

  render(songs: Song[]) {
    if (this.snippet) {
      render(
        html` <dialog
          id="editDanceModal"
          class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transform rounded-xl border-2 border-gray-200 p-9"
        >
          <h2 class="text-2xl">Switch Song for Snippet (${this.snippet.id})</h2>
          <form class="flex max-w-fit flex-col items-center gap-1 py-3">
            <label for="song" class="flex w-full items-center justify-between gap-2">
              <span>Song:</span>
              <select
                class="rounded-md border-2 border-gray-200 p-1 hover:border-gray-300 focus:border-gray-400 focus:shadow"
                name="song"
                type="number"
              >
                ${songs
                  .map((d) => {
                    return `<option value="${d.id}">${d.title}</option>`
                  })
                  .join('')}
              </select>
            </label>
          </form>

          <div class="flex justify-center gap-2">
            <button
              id="cancelSwitchDanceModal"
              class="cursor-pointer rounded-lg bg-gray-100 px-5 py-1 hover:bg-gray-200"
            >
              cancel
            </button>
            <button
              type="submit"
              id="saveSwitchDanceModal"
              class="bg-gray-dark cursor-pointer rounded-lg px-5 py-1 text-white hover:text-white"
            >
              save
            </button>
          </div>
        </dialog>`,
        this
      )

      const modal = document.querySelector('dialog')

      document
        .querySelector('#cancelSwitchDanceModal')
        ?.addEventListener('click', (e) => this.close())
      document.querySelector('#saveSwitchDanceModal')?.addEventListener('click', (e) => {
        this.switchSongForSnippet()
      })

      modal?.addEventListener('click', (event) => {
        if (event.target === modal) {
          this.close()
        }
      })

      addLinks(this)
    }
  }

  switchSongForSnippet() {
    const songId = Number.parseInt(
      (document.querySelector('select[name="song"]') as HTMLSelectElement)?.value
    )

    if (songId) {
      set((model) => {
        model.snippets = model.snippets.map((s) => {
          if (s.id === this.snippet.id) {
            return produce(s, (draft) => {
              draft.songId = songId
            })
          }

          return s
        })
      })
    }
  }

  close() {
    const dialog = this.querySelector('dialog')

    if (dialog) {
      dialog.close()
    }

    set((model) => {
      model.snippetToSwitchSong = -1
    })
  }

  show() {
    const dialog = this.querySelector('dialog')
    if (dialog) {
      dialog.showModal()
    }
  }
}

customElements.define(SwitchSongModal, SwitchSongElement)
