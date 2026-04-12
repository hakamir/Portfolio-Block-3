<script setup lang="ts">
import {ref, onMounted, onBeforeUnmount} from 'vue'
import {CirclePlay, CirclePause, Check, CircleDotDashed} from '@lucide/vue'
import {useAudioPlayerStore} from "@stores"
import Tooltip from "@components/layout/Tooltip.vue";

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
        <Tooltip message="Ready for upload" :icon="CircleDotDashed" iconBgColor="bg-blue-500/50" side="left">
          <CircleDotDashed class="bg-blue-500/50 text-blue-700 p-1 rounded-full w-6 h-6"/>
        </Tooltip>
      </div>
      <div v-else>
        <Tooltip message="Already uploaded on the server" :icon="Check" iconBgColor="bg-lime-500/50"  side="left">
          <Check class="bg-lime-500/50 text-lime-700 p-1 rounded-full w-6 h-6"/>
        </Tooltip>

      </div>
    </div>
    <button @click="togglePlay" class="-m-2 p-2">
      <CirclePlay v-if="!isPlaying" class="max-w-6 h-6 text-blue-700/70"/>
      <CirclePause v-else class="w-6 h-6 text-red-700/70"/>
    </button>
  </div>
  <audio ref="audioRef" :src="props.src" preload="none"/>
</template>