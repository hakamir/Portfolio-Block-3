<script setup lang="ts">

import Card from "@views/portfolio/components/Card.vue";
import AudioPlayer from "@components/AudioPlayer.vue";
import {LoaderCircle} from "@lucide/vue";
import {useAudioStore} from "@stores/audio.ts";
import {onMounted} from "vue";

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

</script>

<template>
  <article>
    <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">
      Discover my albums
    </h2>

    <!-- Loading -->
    <template v-if="audioStore.fetchStatus === 'loading'">
      <Card title="">
        <div class="flex items-center justify-center gap-2">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Loading...</span>
        </div>
      </Card>
    </template>

    <!-- Error -->
    <template v-else-if="audioStore.fetchStatus === 'error'">
      <Card title="Erreur">
        <p>Impossible de charger les albums.</p>
      </Card>
    </template>

    <!-- Success -->
    <template v-else>
      <template v-for="artist in audioStore.artists">
        <Card v-for="album in artist.albums" :title="`${artist.title} - ${album.title}`">
          <AudioPlayer
              v-for="track in album.tracks"
              :title="track.title"
              :src="`${apiUrl}/uploads/audio/${artist.slug}/${album.slug}/${track.src}`"
              :subtitle="`${artist.title} - ${album.title}`"
          />
        </Card>
      </template>
    </template>
  </article>
</template>

<style scoped>

</style>