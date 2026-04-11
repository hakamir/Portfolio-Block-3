<script setup lang="ts">
import {ref, onMounted, onBeforeUnmount} from 'vue'
import {CirclePlay, CirclePause, Check, CircleDotDashed} from '@lucide/vue'
import {useAudioPlayerStore} from "@stores"

const props = defineProps<{ src: string, className?: string, isLocal?: boolean }>()

const playerStore = useAudioPlayerStore()
const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

const togglePlay = () => {
  if (!audioRef.value) return
  if (isPlaying.value) {
    playerStore.pause(audioRef.value)
    audioRef.value.currentTime = 0
    isPlaying.value = false
  } else {
    playerStore.play(audioRef.value)
    isPlaying.value = true
  }
}

const onPause = () => {
  isPlaying.value = false
}

onMounted(() => audioRef.value?.addEventListener('pause', onPause))
onBeforeUnmount(() => audioRef.value?.removeEventListener('pause', onPause))
</script>

<template>
  <div :class="[props.className]">
    <div class="relative group/tooltip w-max">
      <div v-if="isLocal">
        <CircleDotDashed class="bg-blue-500/50 text-blue-700 p-1 rounded-full w-6 h-6"/>
        <div
            class="absolute top-1/2 right-full mr-2 -translate-y-1/2 bg-gray-800/60 backdrop-blur-sm rounded-2xl text-white p-2 text-sm opacity-0 group-hover/tooltip:opacity-100 transition-opacity delay-500 whitespace-nowrap pointer-events-none flex items-center gap-2">
          <CircleDotDashed class="w-8 h-8 border rounded-full bg-blue-500/50 border-gray-300/70 p-1"/>
          Ready for upload
        </div>
      </div>
      <div v-else>
        <Check class="bg-lime-500/50 text-lime-700 p-1 rounded-full w-6 h-6"/>
        <div
            class="absolute top-1/2 right-full mr-2 -translate-y-1/2 bg-gray-800/60 backdrop-blur-sm rounded-2xl text-white p-2 text-sm opacity-0 group-hover/tooltip:opacity-100 transition-opacity delay-500 whitespace-nowrap pointer-events-none flex items-center gap-2">
          <Check class="w-8 h-8 border rounded-full bg-lime-500/50 border-gray-300/70 p-1"/>
          Already uploaded on the server
        </div>
      </div>
    </div>
    <button @click="togglePlay" class="-m-2 p-2">
      <CirclePlay v-if="!isPlaying" class="max-w-6 h-6 text-blue-700/70"/>
      <CirclePause v-else class="w-6 h-6 text-red-700/70"/>
    </button>
  </div>
  <audio ref="audioRef" :src="props.src" preload="none"/>
</template>