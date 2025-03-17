import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'

export async function fetchAllSnippets() {
  const response = await fetch('/api/snippets')
  const snippets = await response.json() as Snippet[]

  set((model) => (model.snippets = snippets))
}
