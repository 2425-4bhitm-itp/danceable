import { Model, set, store } from './model'

import { Snippet } from './snippet/snippet'
import { Dance } from './dance/dance'

import {fetchAllDancesToModel} from 'model/dance/dance-service'
import {fetchAllSnippetsToModel} from 'model/snippet/snippet-service'


export { Model, set, Snippet, Dance, fetchAllDancesToModel, fetchAllSnippetsToModel, store }
