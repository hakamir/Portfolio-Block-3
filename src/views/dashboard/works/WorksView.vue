<script setup lang="ts">

import {useAudioStore} from "@stores";
import {onMounted} from "vue";
import {GripVertical, Upload, Plus} from "@lucide/vue";

const audioStore = useAudioStore();

onMounted(async () => {
  await audioStore.fetchAudios();
})
</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded">Works</h1>
    <div class="border border-gray-200 bg-gray-50 rounded-xl p-6 flex flex-col">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-semibold mb-4">Audio</h2>
        <!-- Add artist button -->
        <button
            class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
          <Plus/>
          New artist
        </button>
      </div>
      <!-- ARTISTS -->
      <div v-for="artist in audioStore.artists" class="">
        <div class="flex items-center justify-between">
          <div class="flex grow items-center">
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
              class="work-add-album-btn group">
            <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
            <span
                class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New album</span>
          </button>
        </div>

        <div class="flex">
          <div class="w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
          <div class="flex flex-col grow">
            <!-- ALBUMS -->
            <div v-for="album in artist.albums">
              <div class="flex items-center">
                <label
                    class="work-label-album group">
                  <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
                  Album
                </label>
                <input type="text"
                       class="work-input-album"
                       :value="album.title">
              </div>
              <div class="flex">
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
                    </div>
                  </div>
                  <!-- Add track button -->
                  <div>
                    <button
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