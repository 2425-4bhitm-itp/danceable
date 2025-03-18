import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { EMPTY_SNIPPET, Snippet } from 'model/snippet/snippet'

export const SnippetComponent = 'snippet-component'

class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden', 'snippet']

  state: Snippet

  constructor() {
    super()
  }

  connectedCallback() {
    this.updateSnippetState(this.getAttribute('snippet')) // initial load of state

    this.render()

    this.querySelector('img.snippet-options').addEventListener('click', (e: MouseEvent) => this.clicked())
  }

  render() {
    render(html`
      <div class="w-full py-2 flex gap-5 items-center select-none" data-id="${this.state.id}">
        <span>
          ${this.state.fileName}
            (${this.state.songSnippetIndex})
        </span>
        <span class="text-gray-400">
          ${this.state.speed} bpm
        </span>
        <div class="flex-1 flex flex-row-reverse gap-2">
          ${this.state.dances.map(
            dance => '<span class="p-0.5 px-3 bg-gray-200 rounded-full">' + dance.name + '</span>',
          ).join('')}
        </div>
        <span class="cursor-pointer w-8">
          <img class="snippet-options w-full" src="/public/icons/options-icon-dark.svg" alt="options button">
        </span>
      </div>
    `, this)

    addLinks(this)
  }

  attributeChangedCallback(name: string, newValue: string | null, oldValue: string) {
    if (name === 'snippet') {
      this.updateSnippetState(newValue)
    }

    this.render()
  }

  clicked() {
    this.dispatchEvent(
      new CustomEvent('snippet-selected', { detail: this.state.id }),
    )
  }

  updateSnippetState(rawSnippet: string) {
    try {
      this.state = rawSnippet ? JSON.parse(rawSnippet) : EMPTY_SNIPPET
    } catch (e) {
      console.log('err when parsing snippet attribute')
      this.state = EMPTY_SNIPPET
    }
  }

  openOptions() {

  }
}

customElements.define(SnippetComponent, SnippetElement)
