<script setup lang="ts">

import {useAudioStore, type Artist, type Album, type Track} from "@stores";
import {onMounted, ref} from "vue";
import {GripVertical, Upload, Plus, ListChevronsDownUp, ListChevronsUpDown, Trash2} from "@lucide/vue";
import { v4 as uuidv4 } from 'uuid';

const audioStore = useAudioStore();

onMounted(async () => {
  await audioStore.fetchAudios();
})

const addArtist = () => {
  audioStore.artists.push({
    _id: uuidv4(),
    artist: '',
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

const toggleArtistCollapse = (id: string) => {
  collapsedArtists.value.has(id) ? collapsedArtists.value.delete(id) : collapsedArtists.value.add(id);
}

const toggleAlbumCollapse = (slug: string) => {
  collapsedAlbums.value.has(slug) ? collapsedAlbums.value.delete(slug) : collapsedAlbums.value.add(slug);
}

</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded">Works</h1>
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
            <button @click="toggleArtistCollapse(artist._id)"
                class="bg-primary-200/50 px-3 py-2 border-l border-y border-gray-300 rounded-l-full group">
              <ListChevronsDownUp v-if="!collapsedArtists.has(artist._id)" class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
              <ListChevronsUpDown v-else class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
            </button>
            <label
                class="work-label-artist group">
              <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
              Artist
            </label>
            <input type="text"
                   class="work-input-artist"
                   :value="artist.artist">
          </div>
          <!-- Add album button -->
          <button
              @click="addAlbum(artist)"
              class="work-add-album-btn group">
            <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
            <span
                class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New album</span>
          </button>
          <button @click="deleteArtist(artist)"
              class="bg-gray-200/50 border-y border-r border-gray-300 px-4 py-2 font-semibold flex items-center gap-1 cursor-pointer select-none transition-transform duration-300 group rounded-r-full">
            <Trash2 class="text-red-700/60 group-hover:text-red-700 group-hover:scale-105 transition"/>
          </button>
        </div>

        <div v-show="!collapsedArtists.has(artist._id)" class="flex">
          <div class="w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
          <div class="flex flex-col grow">
            <!-- ALBUMS -->
            <div v-for="album in artist.albums">
              <div class="flex items-center mt-2">
                <button @click="toggleAlbumCollapse(album.slug)"
                    class="bg-yellow-200/50 px-3 py-2 border-l border-y border-gray-300 rounded-l-full group">
                  <ListChevronsDownUp v-if="!collapsedAlbums.has(album.slug)" class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
                  <ListChevronsUpDown v-else class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
                </button>
                <label class="work-label-album group">
                  <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
                  Album
                </label>
                <input type="text"
                       class="work-input-album"
                       :value="album.title">
                <button @click="deleteAlbum(artist, album)"
                    class="bg-gray-200/50 border-y border-r border-gray-300 px-4 py-2 font-semibold flex items-center gap-1 cursor-pointer select-none transition-transform duration-300 group">
                  <Trash2 class="text-red-700/60 group-hover:text-red-700 group-hover:scale-105 transition"/>
                </button>
              </div>
              <div v-show="!collapsedAlbums.has(album.slug)" class="flex">
                <div class="w-2 bg-yellow-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
                <div class="flex flex-col grow">
                  <!-- TRACKS -->
                  <div v-for="track in album.tracks">
                    <div class="flex items-center">
                      <label
                          class="work-label-track group">
                        <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
                        Track
                      </label>
                      <button
                          class="work-upload-btn group">
                        <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
                      </button>
                      <input type="text"
                             class="work-input-track"
                             :value="track.title">
                      <button @click="deleteTrack(album, track)"
                          class="bg-gray-200/50 border-b border-r border-gray-300 px-4 py-2 font-semibold flex items-center gap-1 cursor-pointer select-none transition-transform duration-300 group">
                        <Trash2 class="text-red-700/60 group-hover:text-red-700 group-hover:scale-105 transition"/>
                      </button>
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