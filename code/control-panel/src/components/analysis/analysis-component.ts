import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

export const Analysis = 'analysis-component'
export const analysisRoute = 'analysis'

class AnalysisElement extends HTMLElement {
  connectedCallback() {
    this.render()
  }

  render() {
    render(html` <div class="mt-8 mb-4 px-2 text-3xl">Analysis</div> `, this)

    addLinks(this)
  }
}

customElements.define(Analysis, AnalysisElement)
