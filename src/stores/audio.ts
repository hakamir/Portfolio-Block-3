import { defineStore } from "pinia";
import { instance } from "@api/axios.ts";
import { ref } from "vue";
import audiosApi from "@api/audios.ts";

interface Track {
  trackNumber: number
  title: string
  src: string
}

interface Album {
  slug: string
  title: string
  tracks: Track[]
}

interface Artist {
  _id: string
  artist: string
  albums: Album[]
}

export const useAudioStore = defineStore('audio', () => {
  const artists = ref<Artist[]>([])
  const loading = ref(false)
  const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')

  const fetchAudios = async () => {
    loading.value = true
    fetchStatus.value = 'loading'
    try {
      const res = await instance.get(audiosApi.getAudios)
      artists.value = res.data
      fetchStatus.value = 'idle'
    } catch (err) {
      fetchStatus.value = 'error'
    } finally {
      loading.value = false
    }
  }

  return { artists, loading, fetchStatus, fetchAudios }
})