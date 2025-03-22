import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'

const SNIPPETS_URL = '/api/snippets'

export async function fetchAllSnippetsToModel() {
  const snippets = await fetchAllSnippets()

  set((model) => model.snippets = snippets)
}

export async function fetchAllSnippets() {
  let snippets: Snippet[] = []

  try {
    const response = await fetch('/api/snippets')

    if (!response.ok) {
      throw new Error(`HTTP error while fetching snippets from ${SNIPPETS_URL}! Status: ${response.status}`)
    }

    snippets = await response.json() as Snippet[]
  } catch (error) {
    console.log(error.toString())
  }

  return snippets
}