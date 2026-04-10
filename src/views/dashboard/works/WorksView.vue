<script setup lang="ts">

import {useAudioStore, type Artist, type Album, type Track} from "@stores";
import {onMounted, ref} from "vue";
import {Plus} from "@lucide/vue";
import {v4 as uuidv4} from 'uuid';
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";
import CollapseButton from "@views/dashboard/works/Components/CollapseButton.vue";
import WorkInput from "@views/dashboard/works/Components/WorkInput.vue";

const audioStore = useAudioStore();

onMounted(async () => {
  await audioStore.fetchAudios();
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

const handleUpload = (src: string | undefined) => console.log(src)

</script>

<template>

  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Works</h1>
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
      <div v-for="artist in audioStore.artists" class="mt-2">
        <div class="flex items-center justify-between">
          <div class="flex grow items-center">
            <!-- Collapse button -->
            <CollapseButton :collapsed="collapsedArtists.has(artist.slug)" @toggle="toggleArtistCollapse(artist.slug)"
                            color="bg-primary-300/30"/>
            <!-- Artist input -->
            <WorkInput type="artist" placeholder="Artist name" v-model="artist.title" />
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
        <div v-show="!collapsedArtists.has(artist.slug)" class="flex">
          <div class="w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
          <div class="flex flex-col grow">
            <div v-for="album in artist.albums">
              <div class="flex items-center mt-2">
                <!-- Collapse button -->
                <CollapseButton :collapsed="collapsedAlbums.has(album.slug)" @toggle="toggleAlbumCollapse(album.slug)"
                                color="bg-yellow-300/30"/>
                <!-- Album input -->
                <WorkInput type="album" placeholder="Album title" v-model="album.title" />
                <!-- Delete album button -->
                <DeleteButton @delete="deleteAlbum(artist, album)" assignedFor="album"/>
              </div>

              <!-- TRACKS -->
              <div v-show="!collapsedAlbums.has(album.slug)" class="flex">
                <div class="w-2 bg-yellow-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
                <div class="flex flex-col grow">
                  <div v-for="track in album.tracks">
                    <div class="flex items-center">
                      <!-- Track Input -->
                      <WorkInput type="track" placeholder="Track title" v-model="track.title" @upload="handleUpload" :src="`${artist.slug}/${album.slug}/${track.src}`" />
                      <!-- Delete track button -->
                      <DeleteButton @delete="deleteTrack(album, track)" assignedFor="track"/>
                    </div>
                  </div>
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>

</style>