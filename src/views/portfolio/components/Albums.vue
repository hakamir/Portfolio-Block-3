<script setup lang="ts">

import Card from "@views/portfolio/components/Card.vue";
import AudioPlayer from "@components/AudioPlayer.vue";
import {LoaderCircle} from "@lucide/vue";
import {useAudioStore} from "@stores/audio.ts";
import {onMounted} from "vue";

const apiUrl = import.meta.env.VITE_API_URL

const audioStore = useAudioStore();
onMounted(async () => {
  await audioStore.fetchAudios();
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
      <template v-for="artist in audioStore.sortedArtists">
        <Card v-for="album in artist.albums" :title="`${artist.artist} - ${album.title}`">
          <AudioPlayer
              v-for="track in album.tracks"
              :title="track.title"
              :src="`${apiUrl}${track.src}`"
              :subtitle="`${artist.artist} - ${album.title}`"
          />
        </Card>
      </template>
    </template>
  </article>
</template>

<style scoped>

</style>