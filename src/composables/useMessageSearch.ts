import {computed} from "vue";
import {type Message} from "@stores";

// Single entry in the search index, representing one searchable item.
export interface MessageSearchEntry {
    id: string
    name: string
    email: string
    preview: string
}

// Search index with a relevance score for a given query.
export interface MessageSearchResult extends MessageSearchEntry {
    score: number
}

/**
 * Returns a match score for a single entry name against the search query.
 * Scoring tiers (case-insensitive):
 *  - 100: exact match
 *  - 60: name starts with the query
 *  - 30: name contains the query anywhere
 *  - 0: no match (entry will be excluded from results)
 */
const scoreMatch = (name: string, query: string): number => {
    const n = name.toLowerCase()
    const q = query.toLowerCase()
    if (n === q) return 100
    if (n.startsWith(q)) return 60
    if (n.includes(q)) return 10
    return 0
}

/**
 * Flattens the full message list into a flat list of `MessageSearchEntry` objects
 * ready to be queried.
 */
const buildEntries = (messages: Message[]): MessageSearchEntry[] =>
    messages.map(m => ({
        id: m._id,
        name: m.name,
        email: m.email,
        preview: m.message.slice(0, 80) + (m.message.length > 80 ? '...' : ''),
    }))


/**
 * Filters and ranks `entries` against `query`, returning up to `limit` results
 * sorted by descending relevance score.
 *
 * Each entry is scored against its name, email, and preview text.
 * The final score is the maximum of these scores.
 */
const runSearch = (query: string, entries: MessageSearchEntry[], limit = 8): MessageSearchResult[] => {
    if (!query.trim()) return []

    return entries.map(entry => {
        const score = Math.max(
            scoreMatch(entry.name, query),
            scoreMatch(entry.email, query),
            scoreMatch(entry.preview, query))
        return {...entry, score}
    })
        .filter(r => r.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, limit)
}

/**
 * Vue composable that wraps the message search index for reactive use in components.
 *
 * `entries` is a computed property that rebuilds the index whenever the underlying
 * `messages` list changes, keeping the search results in sync with the store.
 *
 * @param messages - Getter function returning the current list of messages.
 */
export const useMessageSearch = (messages: () => Message[]) => {
    const entries = computed(() => buildEntries(messages()))
    const search = (query: string, limit = 8): MessageSearchResult[] => runSearch(query, entries.value, limit)
    return {search}
}