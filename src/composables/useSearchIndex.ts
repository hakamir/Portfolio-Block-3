import {computed} from 'vue'
import type {Artist} from "@stores"

/** A single entry in the search index, representing one searchable item. */
export interface SearchEntry {
    /** The category of the item. */
    type: 'track' | 'artist' | 'album' | 'tag'
    /** Unique identifier for the item (e.g. "artistId/albumSlug/trackNumber"). */
    id: string
    /** Display name used for matching and rendering. */
    name: string
    /** Optional subtitle shown below the name (e.g., album and artist for a track). */
    sub: string | null
    /** For tags only: how many tracks carry this tag. Used to boost popular tags. */
    freq?: number
}

/** A search index entry enriched with a relevance score for a given query. */
export interface SearchResult extends SearchEntry {
    /** Relevance score computed from match quality, entry type, and tag frequency. */
    score: number
}

/**
 * Base score added to each result depending on its type.
 * Tags rank highest because they act as genre/mood filters and tend to be
 * more intentional search targets than browsing by artist or album.
 */
const TYPE_BONUS: Record<SearchEntry['type'], number> = {
    tag: 20,
    track: 30,
    artist: 20,
    album: 10,
}

/**
 * Multiplier applied to a tag's frequency when computing its score.
 * More widely used tags receive a higher boost, surfacing popular genres first.
 */
const TAG_FREQ_WEIGHT = 5

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
 * Flattens the full artist/album/track hierarchy into a flat list of
 * `SearchEntry` objects ready to be queried.
 *
 * Tags are deduplicated across the whole dataset and annotated with their
 * total usage frequency so the scorer can favor popular ones.
 */
export const buildEntries = (artists: Artist[]): SearchEntry[] => {
    // First pass: count how many tracks each tag appears on.
    const tagFreq: Record<string, number> = {}
    for (const artist of artists)
        for (const album of artist.albums)
            for (const track of album.tracks)
                for (const tag of track.tags)
                    tagFreq[tag] = (tagFreq[tag] || 0) + 1

    const entries: SearchEntry[] = []
    // Track which tags have already been added to avoid duplicate entries.
    const seenTags = new Set<string>()

    // Second pass: emit one entry per artist, album, track, and unique tag.
    for (const artist of artists) {
        entries.push({type: 'artist', id: artist._id, name: artist.title, sub: null})

        for (const album of artist.albums) {
            entries.push({
                type: 'album',
                id: `${artist._id}/${album.slug}`,
                name: album.title,
                sub: artist.title,
            })

            for (const track of album.tracks) {
                entries.push({
                    type: 'track',
                    id: `${artist._id}/${album.slug}/${track.trackNumber}`,
                    name: track.title,
                    sub: `${album.title} — ${artist.title}`,
                })

                for (const tag of track.tags) {
                    if (!seenTags.has(tag)) {
                        seenTags.add(tag)
                        entries.push({
                            type: 'tag',
                            id: `tag/${tag}`,
                            name: tag,
                            // Subtitle shows the total number of tracks carrying this tag.
                            sub: `${tagFreq[tag]} track${tagFreq[tag] > 1 ? 's' : ''}`,
                            freq: tagFreq[tag],
                        })
                    }
                }
            }
        }
    }

    return entries
}

/**
 * Filters and ranks `entries` against `query`, returning up to `limit` results
 * sorted by descending relevance score.
 *
 * The final score combines:
 *  - match quality (from `scoreMatch`)
 *  - type bonus (tags > tracks > artists > albums)
 *  - tag frequency (popular tags are boosted via `TAG_FREQ_WEIGHT`)
 */
export const runSearch = (query: string, entries: SearchEntry[], limit = 8): SearchResult[] => {
    if (!query.trim()) return []

    const results: SearchResult[] = []

    for (const entry of entries) {
        const matchScore = scoreMatch(entry.name, query)
        // Skip entries that don't match the query at all.
        if (matchScore === 0) continue

        const score =
            matchScore +
            TYPE_BONUS[entry.type] +
            (entry.type === 'tag' ? (entry.freq ?? 1) * TAG_FREQ_WEIGHT : 0)

        results.push({...entry, score})
    }

    return results.sort((a, b) => b.score - a.score).slice(0, limit)
}

/**
 * Vue composable that wraps the search index for reactive use in components.
 *
 * `entries` is a computed property that rebuilds the index whenever the
 * underlying artist data changes, so search results stay in sync with the store.
 *
 * @param artists - Getter function returning the current list of artists.
 */
export const useSearchIndex = (artists: () => Artist[]) => {
    const entries = computed(() => buildEntries(artists()))

    /** Searches the index and returns up to `limit` ranked results. */
    const search = (query: string, limit = 8): SearchResult[] => {
        return runSearch(query, entries.value, limit)
    }

    return {search}
}
