import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { Snippet } from 'model/snippet/snippet'
import { store } from 'model/model'
import { Song } from 'model/song/song'
import { Dance } from 'model/dance/dance'

export const SnippetComponent = 'snippet-component'

export class SnippetElement extends HTMLElement {
  snippet: Snippet

  isOptionsOpen: boolean = false

  constructor() {
    super()
  }

  connectedCallback() {
    store.subscribe((model) => {
      if (this.snippet) {
        this.snippet = model.snippets.find((s) => s.id === this.snippet.id)

        this.render(model.songs, model.dances)
      }
    })
  }

  render(allSongs: Song[], allDances: Dance[]) {
    if (this.snippet) {
      const song = allSongs.find((s) => s.id === this.snippet.songId)

      if (song) {
        const dance = allDances.find((d) => {
          const song = allSongs.find((s) => s.id === this.snippet.songId)

          return d.id === song.danceId
        })

        if (dance) {
          render(
            html`
              <div
                class="flex w-full items-center gap-5 border-t-2 border-t-gray-100 py-1.5 select-none"
              >
                <span> ${song.title} (${this.snippet.id}) </span>
                <span class="text-gray-400"> ${song.speed} bpm </span>
                <div class="flex flex-1 flex-row-reverse gap-2">
                  <span class="rounded-full bg-gray-100 p-0.5 px-3">${dance.name}</span>
                </div>
                <div class="relative w-8">
                  <div
                    hidden
                    class="snippet-options absolute top-0 right-8 flex min-w-12 flex-col rounded-md bg-white p-1 text-nowrap shadow"
                  >
                    <button
                      class="analyse-song-option rounded px-2 py-1 text-left text-purple-500 hover:bg-gray-100"
                    >
                      analyse
                    </button>
                    <button class="edit-song-option rounded px-2 py-1 text-left hover:bg-gray-100">
                      edit song
                    </button>
                    <button
                      class="change-song-option rounded px-2 py-1 text-left hover:bg-gray-100"
                    >
                      switch song
                    </button>
                    <button
                      class="delete-song-option rounded px-2 py-1 text-left text-red-400 hover:bg-gray-100"
                    >
                      delete snippet
                    </button>
                  </div>
                  <button
                    class="snippet-options-button flex aspect-square w-full items-center justify-center rounded-md hover:bg-gray-100"
                  >
                    <img
                      class="w-full"
                      src="/public/svgs/options-icon-dark.svg"
                      alt="options button"
                    />
                  </button>
                </div>
              </div>
            `,
            this
          )
        }

        this.querySelector('.edit-song-option')?.addEventListener('click', (e: MouseEvent) =>
          this.editSong()
        )

        this.querySelector('.change-song-option')?.addEventListener('click', (e: MouseEvent) =>
          this.changeSong()
        )

        this.querySelector('.snippet-options-button')?.addEventListener('click', (e: MouseEvent) =>
          this.optionsClicked()
        )

        this.querySelector('.delete-song-option')?.addEventListener('click', (e: MouseEvent) =>
          this.deleteSong()
        )

        addLinks(this)
      }
    }
  }

  changeSong() {
    this.dispatchEvent(new CustomEvent('change-song', { detail: this.snippet.id }))
  }

  editSong() {
    this.dispatchEvent(new CustomEvent('edit-song', { detail: this.snippet.songId }))
  }

  optionsClicked() {
    this.dispatchEvent(new CustomEvent('snippet-options-clicked', { detail: this.snippet }))

    this.openOrCloseOptions(!this.isOptionsOpen)
  }

  deleteSong() {
    this.dispatchEvent(new CustomEvent('delete-snippet', { detail: this.snippet }))
  }

  openOrCloseOptions(changeOptionsTo: boolean) {
    this.isOptionsOpen = changeOptionsTo

    const optionsElement = this.querySelector('.snippet-options')

    if (optionsElement) {
      if (this.isOptionsOpen) {
        optionsElement.removeAttribute('hidden')
      } else {
        optionsElement.setAttribute('hidden', '')
      }
    }
  }
}

customElements.define(SnippetComponent, SnippetElement)
