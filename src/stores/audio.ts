import {defineStore} from "pinia";
import {instance} from "@api/axios.ts";
import {computed, ref, watch} from "vue";
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
    title: string
    slug: string
    order: number
    albums: Album[]
}

export const useAudioStore = defineStore('audio', () => {
    const artists = ref<Artist[]>([])
    const loading = ref(false)
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')

    const toSlug = (str: string) => str.toLowerCase().trim().replace(/\s+/g, '_')

    const pendingUploads = ref<Map<Track, File>>(new Map())

    watch(() => artists.value, (artists) => {
        artists.forEach(artist => {
            artist.slug = toSlug(artist.title)
            artist.albums.forEach(album => {
                album.slug = toSlug(album.title)
                album.tracks.forEach(track => {
                    track.src = `${toSlug(track.title)}.mp3`
                })
            })
        })
    }, {deep: true})

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

    const checkAudioExists = async (src: string | undefined) => {
        if (!src) return false
        try {
            await instance.head(src)
            return true
        } catch {
            return false
        }
    }

    const uploadTrack = async (file: File, albumSlug: string, track: Track) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('albumSlug', albumSlug)
        formData.append('trackSrc', track.src)
        try {
            await instance.post(audiosApi.uploadAudio, formData)
        } catch (err) {
            console.error('Error uploading track:', err)
        }
    }

    const saveAudios = async () => {
        try {
            // Upload pending tracks
            for (const [track, file] of pendingUploads.value.entries()) {
                const artist = artists.value.find(
                    artist => artist.albums.some(
                        album => album.tracks.includes(track)
                    )
                )
                const album = artist?.albums.find(
                    album => album.tracks.includes(track)
                )
                if (!artist || !album || !track.src) continue

                const formData = new FormData()
                formData.append('file', file)
                formData.append('artistSlug', artist.slug)
                formData.append('albumSlug', album.slug)
                formData.append('trackSrc', track.src)
                await instance.post(audiosApi.uploadAudio, formData)
            }
            pendingUploads.value.clear()

            // Get ids from existing artists
            const existingIds = (await instance.get(audiosApi.getAudios)).data.map((a: Artist) => a._id)

            // If an artist id exists on the server but not in the store, delete it
            const currentIds = artists.value.map(a => a._id).filter(id => id)
            const toDelete = existingIds.filter((id: string) => !currentIds.includes(id))
            for (const id of toDelete) {
                await instance.delete(audiosApi.deleteArtist(id))
            }

            // Save artists
            await instance.put(audiosApi.updateAudios, artists.value)
        } catch (err) {
            console.error('Error saving audios:', err)
        }
    }

    return {artists, sortedArtists, loading, fetchStatus, fetchAudios, checkAudioExists, pendingUploads, uploadTrack, saveAudios}
})