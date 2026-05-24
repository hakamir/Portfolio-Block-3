<script setup lang="ts">
import {useAudioStore, type Artist, type Album, type Track} from "@stores";
import {onMounted, onUnmounted, ref} from "vue";
import {LoaderCircle, Plus, Save, Ban, GripVertical, ChevronDown, Trash2, MoreHorizontal} from "@lucide/vue";
import {v4 as uuidv4} from 'uuid';
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";
import CollapseButton from "@views/dashboard/works/Components/CollapseButton.vue";
import WorkAudioInput from "@views/dashboard/works/Components/WorkAudioInput.vue";
import {VueDraggable} from "vue-draggable-plus";
import CollapseTransition from "@components/CollapseTransition.vue";
import {storeToRefs} from "pinia";

const apiUrl = import.meta.env.VITE_API_URL + '/api'
const audioStore = useAudioStore();
const emit = defineEmits(['TagSelectorToggled'])
const isMobile = ref(false)

const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768;
}

onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  window.addEventListener('click', handleClickOutside)
  await audioStore.fetchAudios()
  audioStore.artists.sort((a, b) => a.order - b.order)
  audioStore.artists.forEach(artist => {
    artist.albums.sort((a, b) => a.order - b.order)
    artist.albums.forEach(album => {
      album.tracks.sort((a, b) => a.trackNumber - b.trackNumber)
    })
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  window.removeEventListener('click', handleClickOutside)
})

const openedMenu = ref<string | null>(null)

const toggleMenu = (key: string) => {
  openedMenu.value = openedMenu.value === key ? null : key
}

const handleClickOutside = () => {
  openedMenu.value = null
}


// Add a new artist with a random slug and empty albums and tracks, order is set to the last artist's order + 1
const addArtist = () => {
  audioStore.artists.push({
    _id: '',
    slug: uuidv4(),
    title: '',
    order: audioStore.artists.length + 1,
    albums: []
  });
}

// Add a new album to a given artist with a random slug and empty tracks, order is set to the last album's order + 1
const addAlbum = (artist: Artist) => {
  artist.albums.push({
    slug: uuidv4(),
    title: '',
    order: artist.albums.length + 1,
    tracks: []
  });
}

// Add a new track to a given album with a random slug and empty tags, trackNumber is set to the last track's trackNumber + 1
const addTrack = (album: Album) => {
  album.tracks.push({
    trackNumber: album.tracks.length + 1,
    title: '',
    src: '',
    tags: [],
  });
}

// Delete an artist and all its albums and tracks
const deleteArtist = (artist: Artist) => {
  const index = audioStore.artists.indexOf(artist);
  audioStore.artists.splice(index, 1);
}

// Delete an album and all its tracks
const deleteAlbum = (artist: Artist, album: Album) => {
  const index = artist.albums.indexOf(album);
  artist.albums.splice(index, 1);
}

// Delete a track from an album
const deleteTrack = (album: Album, track: Track) => {
  const index = album.tracks.indexOf(track);
  album.tracks.splice(index, 1);
  audioStore.removeTrackState(track);
}

const collapsedArtists = ref<Set<string>>(new Set());
const collapsedAlbums = ref<Set<string>>(new Set());

// Collapse the section of an artist
const toggleArtistCollapse = (context: string) => {
  collapsedArtists.value.has(context) ? collapsedArtists.value.delete(context) : collapsedArtists.value.add(context);
}

// Collapse the section of an album
const toggleAlbumCollapse = (slug: string) => {
  collapsedAlbums.value.has(slug) ? collapsedAlbums.value.delete(slug) : collapsedAlbums.value.add(slug);
}


// Handle drag and drop reordering of artists
const reorderArtists = () => {
  audioStore.artists.forEach((artist, index) => {
    artist.order = index + 1
  })
}

// Handle drag and drop reordering of albums within an artist
const reorderAlbums = (artist: Artist) => {
  artist.albums.forEach((album, index) => {
    album.order = index + 1
  })
}

// Handle drag and drop reordering of tracks within an album
const reorderTracks = (album: Album) => {
  album.tracks.forEach((track, index) => {
    track.trackNumber = index + 1;
  })
}

const refreshKey = ref(0);
const {fetchStatus} = storeToRefs(audioStore);

// Save audios then metadata to the database, then refresh the page if it succeeds
const onSave = async () => {
  try {
    if (await audioStore.saveAudios()) {
      await audioStore.fetchAudios()
      refreshKey.value += 1;
    }
  } catch (error) {
    console.error('Error saving audios:', error)
    fetchStatus.value = 'error'
  }
}
</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl md:p-6 flex flex-col">
    <div class="flex justify-between items-center md:mb-4 px-6 pt-4 md:p-0">
      <h2 class="text-2xl font-semibold mb-4">Audios</h2>
      <!-- Add artist button -->
      <button
          @click="addArtist"
          class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
        <Plus/>
        New artist
      </button>
    </div>

    <!-- DESKTOP -->
    <div v-if="!isMobile">
      <VueDraggable
          v-model="audioStore.artists"
          handle=".drag-handle"
          group="artists"
          @update="reorderArtists()"
          class="flex flex-col gap-2">
        <!-- ARTISTS -->
        <div v-for="(artist, artistIndex) in audioStore.artists" class="mt-2" :key="refreshKey">
          <div class="flex items-center justify-between">
            <div class="flex grow items-center">
              <!-- Collapse button -->
              <CollapseButton :collapsed="collapsedArtists.has(`artist-${artistIndex}`)"
                              @toggle="toggleArtistCollapse(`artist-${artistIndex}`)"
                              color="bg-primary-300/30" aria-label="collapse artist"/>
              <!-- Artist input -->
              <WorkAudioInput type="artist" placeholder="Artist name" v-model="artist.title"/>
            </div>
            <!-- Add album button -->
            <button
                @click="addAlbum(artist)"
                class="work-add-album-btn group">
              <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
              <span
                  class="hidden md:block text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New album</span>
            </button>
            <!-- Delete artist button -->
            <DeleteButton @delete="deleteArtist(artist)" customClass="rounded-r-full" assignedFor="artist" aria-label="delete artist"/>
          </div>

          <!-- ALBUMS -->
          <CollapseTransition :show="!collapsedArtists.has(`artist-${artistIndex}`)" customClass="flex">
            <div
                class="hidden md:block w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
            <div class="flex flex-col grow">
              <VueDraggable
                  v-model="artist.albums"
                  handle=".drag-handle"
                  group="albums"
                  @update="reorderAlbums(artist)"
                  class="flex flex-col">
                <div v-for="(album, albumIndex) in artist.albums">
                  <div class="flex items-center mt-2">
                    <!-- Collapse button -->
                    <CollapseButton :collapsed="collapsedAlbums.has(`album-${artistIndex}-${albumIndex}`)"
                                    @toggle="toggleAlbumCollapse(`album-${artistIndex}-${albumIndex}`)"
                                    color="bg-yellow-300/30"
                                    aria-label="collapse album"/>
                    <!-- Album input -->
                    <WorkAudioInput type="album" placeholder="Album title" v-model="album.title"/>
                    <!-- Delete album button -->
                    <DeleteButton @delete="deleteAlbum(artist, album)" customClass="rounded-tr-2xl"
                                  assignedFor="album" aria-label="delete album"/>
                  </div>

                  <!-- TRACKS -->
                  <CollapseTransition :show="!collapsedAlbums.has(`album-${artistIndex}-${albumIndex}`)"
                                      customClass="flex">
                    <div
                        class="hidden md:block w-2 bg-yellow-200/30 border-x border-b border-gray-400/30 mx-4 mb-6 rounded-b-full"/>
                    <div class="flex flex-col grow">
                      <VueDraggable
                          v-model="album.tracks"
                          handle=".drag-handle"
                          group="tracks"
                          @update="reorderTracks(album)"
                          class="flex flex-col">
                        <div v-for="(track, index) in album.tracks" :key="track.trackNumber">
                          <div class="flex items-center">
                            <!-- Track Input -->
                            <WorkAudioInput type="track"
                                            placeholder="Track title"
                                            v-model="track.title"
                                            :src="`${apiUrl}/upload/audio/${artist.slug}/${album.slug}/${track.src}`"
                                            :track="track"
                                            :album="album"
                                            :artist="artist"
                                            @TagSelectorToggled="emit('TagSelectorToggled', track)"
                                            @deleteTrack="deleteTrack(album, track)"
                                            :index="index"
                            />
                          </div>
                        </div>
                      </VueDraggable>
                      <!-- Add track button -->
                      <div>
                        <button
                            @click="addTrack(album)"
                            class="work-add-track-btn group">
                          <Plus class="text-gray-400 group-hover:text-gray-600 group-hover:scale-110 transition"/>
                          <span class="text-sm text-gray-600">Add track</span>
                        </button>
                      </div>
                    </div>
                  </CollapseTransition>
                </div>
              </VueDraggable>
            </div>
          </CollapseTransition>
        </div>
      </VueDraggable>
      <div class="flex justify-end items-center mt-4 gap-4">
        <div v-if="fetchStatus == 'error'" class="flex items-center gap-2 text-red-800 bg-red-100 rounded-full p-2">
          <Ban/>
          <span class="text-sm font-semibold">An error occurred. Some files may not have been uploaded.</span>
        </div>
        <button v-if="fetchStatus == 'idle' || fetchStatus == 'error'" @click="onSave"
                class="px-6 py-2 bg-blue-500 text-white rounded-2xl hover:bg-blue-600 transition flex items-center gap-2">
          <Save class="w-6 h-6"/>
          <span class="font-unbounded">Save</span>
        </button>
        <button v-if="fetchStatus == 'loading'" @click="onSave"
                class="px-6 py-2 bg-gray-700 text-white rounded-2xl transition flex items-center gap-2 cursor-not-allowed!">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Uploading...</span>
        </button>
      </div>
    </div>

    <!-- MOBILE -->
    <div v-else class="flex flex-col">
      <VueDraggable v-model="audioStore.artists"
                    handle=".drag-handle"
                    group="artists"
                    @update="reorderArtists()"
                    class="flex flex-col">
        <!-- ARTISTS -->
        <div v-for="(artist, artistIndex) in audioStore.artists" :key="refreshKey">
          <div
              class="flex items-center outline-none bg-primary-500/20 focus:bg-primary-500/40 hover:bg-primary-500/30 border border-primary-900/20 transition py-3 px-1">
            <label class="drag-handle" aria-label="Reorder artists">
              <GripVertical class="text-gray-400 group-hover:text-gray-500 transition mx-1"/>
            </label>
            <input
                class="w-full focus:bg-white border transition-all duration-300 border-transparent focus:border-gray-300 rounded-md px-2 py-1 mr-2 outline-none"
                v-model="artist.title"
                type="text" placeholder="Artist name"
                aria-label="Artist name input"/>
            <div class="flex items-center gap-2">
              <button @click="toggleArtistCollapse(`artist-${artistIndex}`)" aria-label="Toggle artist collapse">
                <ChevronDown
                    class="transition-transform duration-200 p-1 w-8 h-8 border border-gray-300 rounded-full"
                    :class="collapsedArtists.has(`artist-${artistIndex}`)  ? 'rotate-180 bg-white text-black' : 'bg-white/50 text-gray-400'"/>
              </button>
              <div ref="menuRef" class="relative">
                <button
                    @click.stop="toggleMenu(`artist-${artistIndex}`)"
                    aria-label="Artist options menu"
                    class="bg-white/50 transition p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center hover:bg-white">
                  <MoreHorizontal class="w-4 h-4 text-gray-600"/>
                </button>
                <div v-if="openedMenu === `artist-${artistIndex}`"
                     class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden z-50"
                     aria-label="Artist options menu">
                  <button
                      @click.stop="deleteArtist(artist)"
                      class="w-full px-4 py-3 text-left text-red-600 hover:bg-red-50 transition"
                      aria-label="Delete artist">
                    <Trash2 class="inline-block mr-2 w-5 h-5"/>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
          <CollapseTransition :show="collapsedArtists.has(`artist-${artistIndex}`)" class="flex flex-col">
            <!-- New album button -->
            <button
                @click="addAlbum(artist)"
                class="work-add-album-btn group flex items-center justify-center gap-2 px-4 py-2">
              <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
              <span class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New album</span>
            </button>
            <!-- ALBUMS -->
            <VueDraggable v-model="artist.albums"
                          handle=".drag-handle"
                          group="albums"
                          @update="reorderAlbums(artist)"
                          class="flex flex-col">
              <div v-for="(album, albumIndex) in artist.albums">
                <div
                    class="flex w-full outline-none bg-yellow-500/20 focus:bg-yellow-500/40 hover:bg-yellow-500/30 border border-yellow-900/20 transition py-3 px-1">
                  <!-- Grip -->
                  <label class="drag-handle" aria-label="Reorder albums">
                    <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
                  </label>
                  <!-- Album name -->
                  <input class="w-full bg-white border border-gray-300 rounded-md px-2 py-1" v-model="album.title"
                         type="text" placeholder="Album name"
                         aria-label="Album name input"/>
                  <!-- Collapse button -->
                  <button @click="toggleAlbumCollapse(`album-${artistIndex}-${albumIndex}`)" class="px-2" aria-label="Toggle album collapse">
                    <ChevronDown
                        class="group-hover:text-gray-500 transition p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center"
                        :class="collapsedAlbums.has(`album-${artistIndex}-${albumIndex}`) ? 'rotate-180 bg-white text-black' : 'bg-white/50 text-gray-400'"/>
                  </button>
                  <!-- Options menu -->
                  <div ref="menuRef" class="relative">
                    <button
                        @click.stop="toggleMenu(`album-${artistIndex}-${albumIndex}`)"
                        class="bg-white/50 transition p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center hover:bg-white"
                        aria-label="Album options menu">
                      <MoreHorizontal class="w-4 h-4 text-gray-600"/>
                    </button>
                    <div v-if="openedMenu === `album-${artistIndex}-${albumIndex}`"
                         class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-xl shadow-lg z-50"
                         aria-label="Album options menu">
                      <button
                          @click.stop="deleteAlbum(artist, album)"
                          class="w-full px-4 py-3 text-left text-red-600 hover:bg-red-50 transition"
                          aria-label="Delete album">
                        <Trash2 class="inline-block mr-2 w-5 h-5"/>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
                <CollapseTransition :show="collapsedAlbums.has(`album-${artistIndex}-${albumIndex}`)"
                                    class="flex flex-col">
                  <VueDraggable
                      v-model="album.tracks"
                      handle=".drag-handle"
                      group="tracks"
                      @update="reorderTracks(album)"
                      class="flex flex-col">
                    <div v-for="(track, index) in album.tracks" :key="track.trackNumber">
                      <WorkAudioInput type="track"
                                      placeholder="Track title"
                                      v-model="track.title"
                                      :src="`${apiUrl}/upload/audio/${artist.slug}/${album.slug}/${track.src}`"
                                      :track="track"
                                      :album="album"
                                      :artist="artist"
                                      @TagSelectorToggled="emit('TagSelectorToggled', track)"
                                      @deleteTrack="deleteTrack(album, track)"
                                      :index="index"
                                      :isMobile="true"
                      />
                    </div>
                  </VueDraggable>
                  <!-- New track button -->
                  <button
                      @click="addTrack(album)"
                      class="work-add-album-btn group flex items-center justify-center gap-2 px-4 py-2">
                    <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
                    <span
                        class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New track</span>
                  </button>
                </CollapseTransition>
              </div>
            </VueDraggable>
          </CollapseTransition>
        </div>
      </VueDraggable>
      <div class="flex items-center">
        <div v-if="fetchStatus == 'error'" class="flex items-center gap-2 text-red-800 bg-red-100 rounded-full p-2">
          <Ban/>
          <span class="text-sm font-semibold">An error occurred. Some files may not have been uploaded.</span>
        </div>
        <button v-if="fetchStatus == 'idle' || fetchStatus == 'error'" @click="onSave"
                class="px-6 py-4 w-full bg-black text-white rounded-b-xl transition flex items-center justify-center gap-2">
          <Save class="w-6 h-6"/>
          <span class="font-unbounded">Save</span>
        </button>
        <button v-if="fetchStatus == 'loading'" @click="onSave"
                class="px-6 py-4 w-full bg-gray-700 text-white rounded-b-xl transition flex items-center justify-center gap-2 cursor-not-allowed!">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Uploading...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>