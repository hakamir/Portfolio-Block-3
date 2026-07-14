<script setup lang="ts">
import Header from "./components/layout/header/Header.vue";
import StickyPlayer from "./components/StickyPlayer.vue";
import {useBackgroundStore} from "@stores/background.ts";
import {onMounted} from "vue";

const backgroundStore = useBackgroundStore()

onMounted(async () => {
  await backgroundStore.fetchBackground()
})

</script>

<template>
  <Header></Header>
  <main class="h-screen overflow-y-scroll scroll-smooth">
    <RouterView/>
  </main>
  <StickyPlayer/>
</template>
