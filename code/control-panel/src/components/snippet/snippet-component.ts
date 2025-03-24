import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { Snippet } from 'model/snippet/snippet'

export const SnippetComponent = 'snippet-component'

export class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden']

  state: Snippet

  isOptionsOpen: boolean = false

  constructor(state: Snippet) {
    super()
  }

  connectedCallback() {
    this.render()

    this.querySelector('.snippet-options-button').addEventListener(
      'click',
      (e: MouseEvent) => this.optionsClicked(),
    )
  }

  render() {
    render(html`
      <div class="w-full py-1.5 flex gap-5 items-center select-none border-t-gray-100 border-t-2"
           data-id="${this.state.id}">
        <span>
          ${this.state.fileName}
            (${this.state.songSnippetIndex})
        </span>
        <span class="text-gray-400">
          ${this.state.speed} bpm
        </span>
        <div class="flex-1 flex flex-row-reverse gap-2">
          ${this.state.song.dances.map(
            dance => '<span class="p-0.5 px-3 bg-gray-100 rounded-full">' + dance.name + '</span>',
          ).join('')}
        </div>
        <div class="w-8 relative">
          <modal hidden
                 class="snippet-options p-1 bg-white shadow absolute top-0 right-8 rounded-md flex flex-col min-w-12 text-nowrap">
            <span class="hover:bg-gray-100 px-2 py-1 rounded text-purple-500">analyse</span>
            <span class="hover:bg-gray-100 px-2 py-1 rounded">add dance</span>
            <span class="hover:bg-gray-100 px-2 py-1 rounded">remove dance</span>
            <span class="hover:bg-gray-100 px-2 py-1 rounded">rename song</span>
            <span class="hover:bg-gray-100 px-2 py-1 rounded">edit</span>
            <span class="hover:bg-gray-100 px-2 py-1 rounded text-red-400">remove</span>
          </modal>
          <div class="w-full snippet-options-button aspect-square rounded-md hover:bg-gray-100 flex justify-center items-center">
            <img class="w-full" src="/public/svgs/options-icon-dark.svg" alt="options button">
          </div>
        </div>
      </div>
    `, this)

    addLinks(this)
  }

  optionsClicked() {
    this.dispatchEvent(
      new CustomEvent('snippet-option-clicked', { detail: this.state }),
    )

    this.openOrCloseOptions(!this.isOptionsOpen)
  }

  openOrCloseOptions(changeOptionsTo: boolean) {
    this.isOptionsOpen = changeOptionsTo

    const optionsElement = this.querySelector('modal.snippet-options')

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
