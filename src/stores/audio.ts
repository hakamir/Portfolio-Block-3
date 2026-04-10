import {defineStore} from "pinia";
import {instance} from "@api/axios.ts";
import {computed, ref} from "vue";
import audiosApi from "@api/audios.ts";

export interface Track {
    trackNumber: number
    title: string
    src: string
}

export interface Album {
    slug: string
    title: string
    order: number
    tracks: Track[]
}

export interface Artist {
    _id: string
    artist: string
    albums: Album[]
}

export const useAudioStore = defineStore('audio', () => {
    const artists = ref<Artist[]>([])
    const loading = ref(false)
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')

    const sortedArtists = computed<Artist[]>(() => artists.value.map((artist: Artist) => ({
        ...artist,
        albums: [...artist.albums]
            .sort((a, b) => a.order - b.order)
            .map(album => ({
                ...album,
                tracks: [...album.tracks].sort((a, b) => a.trackNumber - b.trackNumber)
            }))
    })))

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

    return {artists, sortedArtists, loading, fetchStatus, fetchAudios}
})