<script setup lang="ts">
import Header from "./components/layout/header/Header.vue";
import StickyPlayer from "./components/StickyPlayer.vue";
import {onMounted} from "vue";
import {useAuthStore} from "@stores";

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.refresh()
})
</script>

<template>
  <Header></Header>
  <main class="h-screen overflow-y-scroll scroll-smooth">
    <RouterView/>
  </main>
  <StickyPlayer/>
</template>
