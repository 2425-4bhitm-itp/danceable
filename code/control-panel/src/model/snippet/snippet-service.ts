import { set } from 'model/model'
import { Snippet } from 'model/snippet/snippet'
import { Song } from 'model/song/song'

const SNIPPETS_URL = '/api/snippets'

export async function fetchAllSnippetsToModel() {
  const snippets = await fetchAllSnippets()

  set((model) => (model.snippets = snippets))
}

export async function patchSnippet(snippet: Snippet) {
  console.log('helloooo')
  try {
    const response = await fetch(`${SNIPPETS_URL}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(snippet),
    })

    if (!response.ok) {
      throw new Error(
        `HTTP error while updating snippet with ID ${snippet.id}! Status: ${response.status}`
      )
    }

    return response
  } catch (error) {
    console.error(error.toString())
    throw error
  }
}

export async function fetchAllSnippets() {
  let snippets: Snippet[] = []

  try {
    const response = await fetch('/api/snippets')

    if (!response.ok) {
      throw new Error(
        `HTTP error while fetching snippets from ${SNIPPETS_URL}! Status: ${response.status}`
      )
    }

    snippets = (await response.json()) as Snippet[]
  } catch (error) {
    console.log(error.toString())
  }

  return snippets
}

export async function deleteSnippet(id: number) {
  try {
    const response = await fetch(`${SNIPPETS_URL}/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error while deleting snippet with ID ${id}! Status: ${response.status}`)
    }

    return response
  } catch (error) {
    console.error(error.toString())
    throw error
  }
}
