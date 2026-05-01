<script setup lang="ts">
import {useAudioStore} from '@stores'
import {Trash2, Music, Music2, Disc, PackageOpen} from '@lucide/vue'
import {computed, onMounted, ref} from "vue";

interface OrphanAudio {
  artist: string;
  album: string;
  track: string;
  src: string;
}

const audioStore = useAudioStore()
const selectedOrphans = ref<string[]>([])
const emit = defineEmits<{ requestDelete: [srcs: string[]] }>()

const orphansUrl = ref<string[]>([])
const orphans = ref<OrphanAudio[]>([])

onMounted(async () => {
  await audioStore.fetchOrphans()
      .then(() => {
        orphansUrl.value = audioStore.orphans
        formatData()
      })
      .catch(error => console.error('Error fetching orphans:', error))
})

const groupedOrphans = computed(() => {
  return orphans.value.reduce((acc, orphan) => {
    if (!acc[orphan.artist]) acc[orphan.artist] = {}
    if (!acc[orphan.artist][orphan.album]) acc[orphan.artist][orphan.album] = []
    acc[orphan.artist][orphan.album].push(orphan)
    return acc
  }, {} as Record<string, Record<string, OrphanAudio[]>>)
})

const toggleSelectAll = () => {
  if (selectedOrphans.value.length === orphans.value.length) {
    selectedOrphans.value = []
  } else {
    selectedOrphans.value = orphans.value.map(o => o.src)
  }
}

const toggleSelectArtist = (artistName: string) => {
  const artistSrcs = Object.values(groupedOrphans.value[artistName])
      .flat()
      .map(o => o.src)

  const allSelected = artistSrcs.every(src => selectedOrphans.value.includes(src))

  if (allSelected) {
    selectedOrphans.value = selectedOrphans.value.filter(src => !artistSrcs.includes(src))
  } else {
    selectedOrphans.value = [...new Set([...selectedOrphans.value, ...artistSrcs])]
  }
}

const toggleSelectAlbum = (artistName: string, albumName: string) => {
  const albumSrcs = groupedOrphans.value[artistName][albumName].map(o => o.src)

  const allSelected = albumSrcs.every(src => selectedOrphans.value.includes(src))

  if (allSelected) {
    selectedOrphans.value = selectedOrphans.value.filter(src => !albumSrcs.includes(src))
  } else {
    selectedOrphans.value = [...new Set([...selectedOrphans.value, ...albumSrcs])]
  }
}

const toggleSelectTrack = (src: string) => {
  if (selectedOrphans.value.includes(src)) {
    selectedOrphans.value = selectedOrphans.value.filter(s => s !== src)
  } else {
    selectedOrphans.value = [...selectedOrphans.value, src]
  }
}

const isArtistSelected = (artistName: string) => {
  const artistSrcs = Object.values(groupedOrphans.value[artistName]).flat().map(o => o.src)
  return artistSrcs.every(src => selectedOrphans.value.includes(src))
}

const isAlbumSelected = (artistName: string, albumName: string) => {
  const albumSrcs = groupedOrphans.value[artistName][albumName].map(o => o.src)
  return albumSrcs.every(src => selectedOrphans.value.includes(src))
}

const formatData = () => {
  orphans.value = orphansUrl.value.map(url => {
    const [artistSlug, albumSlug, trackSrc] = url.split('/')
    const toLabel = (slug: string) => slug
        .replace(/\.[^.]+$/, '')     // retire l'extension (.mp3)
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')

    return {
      artist: toLabel(artistSlug),
      album: toLabel(albumSlug),
      track: toLabel(trackSrc),
      src: url
    } as OrphanAudio
  })
}
</script>

<template>
  <!-- Orphan audios -->
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Orphan audios</h2>
        <p class="text-sm text-gray-500 mt-1">Files present on the server but not linked to any track.</p>
      </div>
    </div>

    <!-- No orphans -->
    <div v-if="orphans.length === 0"
         class="flex flex-col items-center justify-center py-8 gap-2">
      <PackageOpen class="w-10 h-10 text-gray-400"/>
      <span class="text-md text-gray-500 font-unbounded">No orphan audios found...</span>
    </div>

    <!-- Orphans list -->
    <div v-else class="flex flex-col gap-2">

      <!-- Select all -->
      <div class="flex justify-between items-center mb-2">
        <label
            class="bg-gray-200 flex items-center gap-2 text-gray-700 cursor-pointer select-none border border-gray-200 rounded-xl px-4 py-2 has-[input:checked]:bg-blue-400 has-[input:checked]:text-white transition">
          <input type="checkbox"
                 :checked="selectedOrphans.length === orphans.length"
                 @change="toggleSelectAll"
                 class="hidden"/>
          Select all ({{ selectedOrphans.length }} / {{ orphans.length }})
        </label>
        <!-- Delete selected -->
        <button
            v-if="selectedOrphans.length > 0"
            @click="emit('requestDelete', selectedOrphans)"
            class="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-200 text-red-800 font-semibold border border-red-200 hover:bg-red-600 hover:text-white transition group">
          <Trash2 class="w-6 h-6"/>
          Delete selected
          <span class="w-6 h-6 flex items-center justify-center border rounded-full text-sm bg-red-100 group-hover:bg-red-700 transition">
            {{ selectedOrphans.length }}
          </span>
        </button>
      </div>

      <!-- Group by artist -->
      <div v-for="(albumGroup, artistName) in groupedOrphans" :key="artistName"
           class="border border-gray-200 rounded-xl overflow-hidden">
        <!-- Artist header -->
        <div @click="toggleSelectArtist(artistName)"
             class="px-4 py-2 flex items-center gap-2 border-b border-gray-200 hover:bg-primary-600/30 cursor-pointer transition select-none"
             :class="isArtistSelected(artistName) ? 'bg-primary-600/50' : 'bg-primary-200/30'">
          <Music class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transtion"
                 :class="isArtistSelected(artistName) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
          <span :class="isArtistSelected(artistName) ? 'font-semibold' : 'font-medium'">{{ artistName }}</span>
        </div>

        <!-- Albums -->
        <div v-for="(tracks, albumName) in albumGroup" :key="albumName">
          <!-- Album header -->
          <div @click="toggleSelectAlbum(artistName, albumName)"
               class="px-6 py-2 flex items-center gap-2 border-b border-gray-100 cursor-pointer hover:bg-yellow-200/50 transition select-none"
               :class="isAlbumSelected(artistName, albumName) ? 'bg-yellow-300/50' : 'bg-yellow-200/80'">
            <Disc class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transition"
                  :class="isAlbumSelected(artistName, albumName) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
            <span :class="isArtistSelected(artistName) ? 'font-semibold' : 'font-medium'">{{ albumName }}</span>
          </div>

          <!-- Tracks -->
          <div v-for="orphan in tracks" :key="orphan.src"
               @click="toggleSelectTrack(orphan.src)"
               class="flex items-center gap-3 px-8 py-2 hover:bg-orange-100 transition border-b border-gray-100 last:border-0 cursor-pointer select-none"
               :class="selectedOrphans.includes(orphan.src) ? 'bg-orange-200/80' : 'bg-orange-200/50'">
            <Music2 class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transition"
                    :class="selectedOrphans.includes(orphan.src) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
            <span :class="selectedOrphans.includes(orphan.src) ? 'font-semibold' : 'font-medium'">{{
                orphan.track
              }}</span>
            <span class="text-xs text-gray-400 ml-auto font-mono">{{ orphan.src }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>