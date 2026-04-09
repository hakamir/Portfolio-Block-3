<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import AudioPlayer from "@components/AudioPlayer.vue";
import Card from "@views/portfolio/components/Card.vue";
import {useAudioStore} from "@stores/audio.ts";
import {onMounted} from "vue";
import {LoaderCircle} from "@lucide/vue";
import ProgressiveImage from "@components/ProgressiveImage.vue";

const apiUrl = import.meta.env.VITE_API_URL
const audioStore = useAudioStore();
onMounted(async () => {
  await audioStore.fetchAudios();
})
</script>

<template>
  <div class="relative min-h-screen flex flex-col">
    <ProgressiveImage src512="./src/assets/img/gallery/background/gallery_0001-512.webp"
                      src1024="./src/assets/img/gallery/background/gallery_0001-1024.webp"
                      src2048="./src/assets/img/gallery/background/gallery_0001-2048.webp"
                      alt="Portfolio Background"
                      class="fixed inset-0 w-full h-full object-cover -z-20"
    />
    <div class="fixed inset-0 bg-linear-180 from-black/0 to-black -z-10"></div>

    <section class="flex-1 pt-28 pb-16 md:pt-48 px-8 md:px-32 text-white">
      <div class="container mx-auto">
        <h1 class="hero-title text-white text-shadow-[0_0_40px_rgba(0,0,0,1)] font-unbounded mb-36 mt-16 md:mt-0">
          <span>Explore</span>
          <span>a brand new</span>
          <span>Horizon</span>
        </h1>
        <article>
          <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">Discover my
            albums</h2>

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
      </div>
    </section>

    <Footer/>
  </div>
</template>