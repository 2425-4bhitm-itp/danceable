import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'

export async function fetchAllSnippetsToModel() {
  const snippets = await fetchAllSnippets()

  set((model) => (model.snippets = snippets))
}


export async function fetchAllSnippets() {
  const response = await fetch('/api/snippets')
  return await response.json() as Snippet[]
}
