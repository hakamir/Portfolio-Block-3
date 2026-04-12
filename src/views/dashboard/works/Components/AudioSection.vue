<script setup lang="ts">
import {useAudioStore, type Artist, type Album, type Track} from "@stores";
import {onMounted, ref} from "vue";
import {Plus, Save} from "@lucide/vue";
import {v4 as uuidv4} from 'uuid';
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";
import CollapseButton from "@views/dashboard/works/Components/CollapseButton.vue";
import WorkInput from "@views/dashboard/works/Components/WorkInput.vue";
import {VueDraggable} from "vue-draggable-plus";
import CollapseTransition from "@components/CollapseTransition.vue";

const apiUrl = import.meta.env.VITE_API_URL
const audioStore = useAudioStore();

onMounted(async () => {
  await audioStore.fetchAudios()
  audioStore.artists.sort((a, b) => a.order - b.order)
  audioStore.artists.forEach(artist => {
    artist.albums.sort((a, b) => a.order - b.order)
    artist.albums.forEach(album => {
      album.tracks.sort((a, b) => a.trackNumber - b.trackNumber)
    })
  })
})

const addArtist = () => {
  audioStore.artists.push({
    _id: '',
    slug: uuidv4(),
    title: '',
    order: audioStore.artists.length + 1,
    albums: []
  });
}

const addAlbum = (artist: Artist) => {
  artist.albums.push({
    slug: uuidv4(),
    title: '',
    order: artist.albums.length + 1,
    tracks: []
  });
}

const addTrack = (album: Album) => {
  album.tracks.push({
    trackNumber: album.tracks.length + 1,
    title: '',
    src: '',
  });
}

const deleteArtist = (artist: Artist) => {
  const index = audioStore.artists.indexOf(artist);
  audioStore.artists.splice(index, 1);
}

const deleteAlbum = (artist: Artist, album: Album) => {
  const index = artist.albums.indexOf(album);
  artist.albums.splice(index, 1);
}

const deleteTrack = (album: Album, track: Track) => {
  const index = album.tracks.indexOf(track);
  album.tracks.splice(index, 1);
}

const collapsedArtists = ref<Set<string>>(new Set());
const collapsedAlbums = ref<Set<string>>(new Set());

const toggleArtistCollapse = (slug: string) => {
  collapsedArtists.value.has(slug) ? collapsedArtists.value.delete(slug) : collapsedArtists.value.add(slug);
}

const toggleAlbumCollapse = (slug: string) => {
  collapsedAlbums.value.has(slug) ? collapsedAlbums.value.delete(slug) : collapsedAlbums.value.add(slug);
}

const reorderTracks = (album: Album) => {
  album.tracks.forEach((track, index) => {
    track.trackNumber = index + 1;
  })
}

const reorderAlbums = (artist: Artist) => {
  artist.albums.forEach((album, index) => {
    album.order = index + 1
  })
}

const reorderArtists = () => {
  audioStore.artists.forEach((artist, index) => {
    artist.order = index + 1
  })
}

const refreshKey = ref(0);

const onSave = async () => {
  try {
    await audioStore.saveAudios()
    await audioStore.fetchAudios()
    refreshKey.value += 1;
  } catch (error) {
    console.error('Error saving audios:', error)
  }
}
</script>

<template>
<div class="border border-gray-200 bg-gray-50 rounded-xl p-6 flex flex-col">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-semibold mb-4">Audio</h2>
        <!-- Add artist button -->
        <button
            @click="addArtist"
            class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
          <Plus/>
          New artist
        </button>
      </div>
      <!-- ARTISTS -->
      <VueDraggable
          v-model="audioStore.artists"
          handle=".drag-handle"
          group="artists"
          @update="reorderArtists()"
          class="flex flex-col gap-2">
        <div v-for="artist in audioStore.artists" class="mt-2" :key="refreshKey">
          <div class="flex items-center justify-between">
            <div class="flex grow items-center">
              <!-- Collapse button -->
              <CollapseButton :collapsed="collapsedArtists.has(artist.slug)" @toggle="toggleArtistCollapse(artist.slug)"
                              color="bg-primary-300/30"/>
              <!-- Artist input -->
              <WorkInput type="artist" placeholder="Artist name" v-model="artist.title"/>
            </div>
            <!-- Add album button -->
            <button
                @click="addAlbum(artist)"
                class="work-add-album-btn group">
              <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
              <span
                  class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New album</span>
            </button>
            <!-- Delete artist button -->
            <DeleteButton @delete="deleteArtist(artist)" customClass="rounded-r-full" assignedFor="artist"/>
          </div>

          <!-- ALBUMS -->
          <CollapseTransition :show="!collapsedArtists.has(artist.slug)" customClass="flex">
            <div class="w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
            <div class="flex flex-col grow">
              <VueDraggable
                  v-model="artist.albums"
                  handle=".drag-handle"
                  group="albums"
                  @update="reorderAlbums(artist)"
                  class="flex flex-col">
                <div v-for="album in artist.albums">
                  <div class="flex items-center mt-2">
                    <!-- Collapse button -->
                    <CollapseButton :collapsed="collapsedAlbums.has(album.slug)"
                                    @toggle="toggleAlbumCollapse(album.slug)"
                                    color="bg-yellow-300/30"/>
                    <!-- Album input -->
                    <WorkInput type="album" placeholder="Album title" v-model="album.title"/>
                    <!-- Delete album button -->
                    <DeleteButton @delete="deleteAlbum(artist, album)" customClass="rounded-tr-2xl"
                                  assignedFor="album"/>
                  </div>

                  <!-- TRACKS -->
                  <CollapseTransition :show="!collapsedAlbums.has(album.slug)" customClass="flex">
                    <div
                        class="w-2 bg-yellow-200/30 border-x border-b border-gray-400/30 mx-4 mb-6 rounded-b-full"/>
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
                            <WorkInput type="track"
                                       placeholder="Track title"
                                       v-model="track.title"
                                       :src="`${apiUrl}/uploads/audio/${artist.slug}/${album.slug}/${track.src}`"
                                       :track="track"
                            />
                            <!-- Delete track button -->
                            <DeleteButton @delete="deleteTrack(album, track)" assignedFor="track"
                                          :customClass="index === album.tracks.length - 1 ? 'rounded-br-2xl' : ''"/>
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
        <div class="flex justify-end mt-4">
          <button @click="onSave"
                  class="px-6 py-2 bg-blue-500 text-white rounded-2xl hover:bg-blue-600 transition flex items-center gap-2">
            <Save class="w-6 h-6"/>
            <span class="font-unbounded">Save</span>
          </button>
        </div>
      </VueDraggable>
    </div>
</template>

<style scoped>

</style>