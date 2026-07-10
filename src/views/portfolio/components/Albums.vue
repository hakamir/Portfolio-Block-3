<script setup lang="ts">
import Card from "@views/portfolio/components/Card.vue"
import AudioPlayer from "@components/AudioPlayer.vue"
import {LoaderCircle, Ban} from "@lucide/vue"
import {useArtistsStore} from "@stores/artists.ts"
import {useSearchStore} from "@stores/search.ts"
import {onMounted, computed} from "vue"
import AudioSearchEngine from "@views/portfolio/components/AudioSearchEngine.vue"

const apiUrl = import.meta.env.VITE_API_URL + '/api'
const artistsStore = useArtistsStore()
const searchStore = useSearchStore()

onMounted(async () => {
  await artistsStore.fetchArtists("public")
  artistsStore.artists.sort((a, b) => a.order - b.order)
  artistsStore.artists.forEach(artist => {
    artist.albums.sort((a, b) => a.order - b.order)
    artist.albums.forEach(album => {
      album.tracks.sort((a, b) => a.trackNumber - b.trackNumber)
    })
  })
})

const filteredArtists = computed(() => {
  const filters = searchStore.activeFilters

  // Show all artists if no filters are active
  if (filters.length === 0) return artistsStore.artists

  // Partition active filters by type into Sets for O(1) lookups below.
  // Each Set is empty when no filter of that type is active, which signals
  // "don't restrict on this dimension" in the filtering steps that follow.
  const artistIds = new Set(filters.filter(f => f.type === 'artist').map(f => f.id))
  const albumIds  = new Set(filters.filter(f => f.type === 'album').map(f => f.id))
  const trackIds  = new Set(filters.filter(f => f.type === 'track').map(f => f.id))
  const tagNames  = new Set(filters.filter(f => f.type === 'tag').map(f => f.name))

  return artistsStore.artists
    // Keep artists that are explicitly selected, or all if no artist filter is active
    .filter(artist => artistIds.size === 0 || artistIds.has(artist._id))
    .map(artist => ({
      ...artist,
      albums: artist.albums
        // Keep albums that are explicitly selected, or all if no album filter is active
        // Album IDs are composite ("artistId/albumSlug") to guarantee global uniqueness
        .filter(album => albumIds.size === 0 || albumIds.has(`${artist._id}/${album.slug}`))
        .map(album => ({
          ...album,
          tracks: album.tracks.filter(track => {
            // If a track filter is active, the track's composite ID must be in the set
            // Track IDs are composite ("artistId/albumSlug/trackNumber").
            if (trackIds.size > 0 && !trackIds.has(`${artist._id}/${album.slug}/${track.trackNumber}`)) return false
            // If a tag filter is active, the track must carry at least one of the selected tags
            return !(tagNames.size > 0 && !track.tags.some(t => tagNames.has(t)))
          })
        }))
        // Drop albums that have no remaining tracks after filtering
        .filter(album => album.tracks.length > 0)
    }))
    // Drop artists that have no remaining albums after filtering
    .filter(artist => artist.albums.length > 0)
})
</script>

<template>
  <article>
    <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">
      Discover my albums
    </h2>
    <AudioSearchEngine/>

    <template v-if="artistsStore.fetchStatus === 'loading'">
      <Card title="">
        <div class="flex items-center justify-center gap-2">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Loading...</span>
        </div>
      </Card>
    </template>

    <template v-else-if="artistsStore.fetchStatus === 'error'">
      <Card title="Error">
        <div class="flex gap-4">
          <Ban/>
          <p>Unable to load albums...</p>
        </div>
      </Card>
    </template>

    <template v-else>
      <Card v-if="filteredArtists.length === 0" title="">
        <p class="text-center text-gray-400">No results for these filters.</p>
      </Card>

      <template v-else>
        <template v-for="artist in filteredArtists" :key="artist._id">
          <Card
              v-for="album in artist.albums"
              :key="album.slug"
              :title="`${artist.title} - ${album.title}`"
          >
            <AudioPlayer
                v-for="track in album.tracks"
                :key="track.trackNumber"
                :title="track.title"
                :tags="track.tags"
                :src="`${apiUrl}/upload/audio/${artist.slug}/${album.slug}/${track.src}`"
                :subtitle="`${artist.title} - ${album.title}`"
            />
          </Card>
        </template>
      </template>
    </template>
  </article>
</template>