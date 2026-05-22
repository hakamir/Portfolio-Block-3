<script setup lang="ts">
import {ref, onMounted, onBeforeUnmount} from 'vue'
import {CirclePlay, CirclePause, Check, CircleDotDashed, Loader} from '@lucide/vue'
import {useAudioPlayerStore} from "@stores"
import Tooltip from "@components/layout/Tooltip.vue";

const props = defineProps<{
  src: string,
  className?: string,
  status?: string
  title?: string
  subtitle?: string
  isMobile?: boolean
}>()

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
    playerStore.play(audioRef.value, {title: props.title || 'Unknown', subtitle: props.subtitle || '', src: props.src})
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
    <!-- Mobile -->
    <div v-if="isMobile" class="relative w-max">
      <div v-if="status === 'uploading'" class="flex items-center gap-2">
        <span class="text-sm font-light font-unbounded text-gray-600">Uploading</span>
        <Loader class="bg-yellow-500/50 text-yellow-700 p-1 rounded-full w-6 h-6 animate-spin"/>
      </div>
      <div v-else-if="status === 'pending'" class="flex items-center gap-2">
        <span class="text-sm font-light font-unbounded text-gray-600">Pending</span>
        <CircleDotDashed class="bg-blue-500/50 text-blue-700 p-1 rounded-full w-6 h-6"/>
      </div>
      <div v-else-if="status === 'uploaded'" class="flex items-center gap-2">
        <span class="text-sm font-light font-unbounded text-gray-600">Uploaded</span>
        <Check class="bg-lime-500/50 text-lime-700 p-1 rounded-full w-6 h-6"/>
      </div>
      <div v-else class="flex items-center gap-2">
        <span class="text-sm font-light font-unbounded text-gray-600">No file</span>
      </div>
    </div>

    <!-- Desktop -->
    <div v-else class="relative group/tooltip w-max">
      <div v-if="status === 'uploading'">
        <Tooltip message="Uploading..." :icon="Loader" iconBgColor="bg-yellow-500/50" side="left">
          <Loader class="bg-yellow-500/50 text-yellow-700 p-1 rounded-full w-6 h-6 animate-spin"/>
        </Tooltip>
      </div>
      <div v-else-if="status === 'pending'">
        <Tooltip message="Ready for upload" :icon="CircleDotDashed" iconBgColor="bg-blue-500/50" side="left">
          <CircleDotDashed class="bg-blue-500/50 text-blue-700 p-1 rounded-full w-6 h-6"/>
        </Tooltip>
      </div>
      <div v-else-if="status === 'uploaded'">
        <Tooltip message="Already uploaded on the server" :icon="Check" iconBgColor="bg-lime-500/50" side="left">
          <Check class="bg-lime-500/50 text-lime-700 p-1 rounded-full w-6 h-6"/>
        </Tooltip>
      </div>
    </div>
    <button @click="togglePlay" class="-m-2 p-2" aria-label="Play/Pause">
      <CirclePlay v-if="!isPlaying" class="max-w-6 h-6 text-blue-700/70"/>
      <CirclePause v-else class="w-6 h-6 text-red-700/70"/>
    </button>
  </div>
  <audio ref="audioRef" :src="props.src" preload="none"/>
</template>