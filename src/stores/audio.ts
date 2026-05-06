import {defineStore} from "pinia";
import {instance} from "@api/axios.ts";
import {ref, watch} from "vue";
import audiosApi from "@api/audios.ts";

export interface Track {
    trackNumber: number
    title: string
    src: string
    tags: string[]
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
    const isSubmitted = ref(false);
    const uploadedFileName = ref<string | undefined>(undefined);
    const orphans = ref<string[]>([])

    // Convert string to slug format ("Track Title" to "track_title")
    const toSlug = (str: string) => str.toLowerCase().trim().replace(/\s+/g, '_')

    const pendingUploads = ref<Map<Track, File>>(new Map())

    watch(() => artists.value, (artists) => {
        isSubmitted.value = false;
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

    // Validate: ensure no artist, album, or track has an empty title
    const hasEmptyFields = (): boolean => {
        return artists.value.some(artist =>
            !artist.title?.trim() ||
            artist.albums.some(album =>
                !album.title?.trim() ||
                album.tracks.some(track =>
                    !track.title?.trim()
                )
            )
        )
    }

    // Upload all pending audio files
    const uploadPendingAudios = async () => {
        for (const [track, file] of pendingUploads.value.entries()) {
            const {artist, album} = findTrackContext(track)
            // Skip if required data is missing
            if (!artist || !album || !track.src) continue

            const formData = new FormData()
            formData.append('file', file)
            formData.append('artistSlug', artist.slug)
            formData.append('albumSlug', album.slug)
            formData.append('trackSrc', track.src)
            // Store current file name for UI feedback during upload
            uploadedFileName.value = file.name
            await instance.post(audiosApi.uploadAudio, formData)
        }
        // Clear upload state after all files are processed
        pendingUploads.value.clear()
        uploadedFileName.value = undefined
    }

    // Find corresponding artist and album for the track
    const findTrackContext = (track: Track) => {
        const artist = artists.value.find(artist =>
            artist.albums.some(album =>
                album.tracks.includes(track)
            )
        )
        const album = artist?.albums.find(album =>
            album.tracks.includes(track)
        )
        return {artist, album}
    }

    const syncDeletedArtists = async () => {
        // Fetch existing artists from server to detect deletions
        const existingIds = (await instance.get(audiosApi.getAudios))
            .data.map((a: Artist) => a._id)

        // Compute artists that exist on server but were removed locally
        const currentIds = artists.value.map(a => a._id).filter(Boolean)
        const toDelete = existingIds.filter((id: string) => !currentIds.includes(id))

        // Delete removed artists from server
        for (const id of toDelete) {
            await instance.delete(audiosApi.deleteArtist(id))
        }
    }

    const saveAudios = async () => {
        // Mark form as submitted and set loading state
        isSubmitted.value = true;
        fetchStatus.value = 'loading';

        // Abort if validation fails
        if (hasEmptyFields()) {
            return false
        }
        // Upload pending audios
        await uploadPendingAudios()
        // Sync deleted artists
        await syncDeletedArtists()
        // Persist current artists state to server
        await instance.put(audiosApi.updateAudios, artists.value)

        // Reset loading state
        fetchStatus.value = 'idle';
        return true;
    }

    const fetchOrphans = async () => {
        try {
            const res = await instance.get(audiosApi.getOrphans)
            orphans.value = res.data
        } catch (err) {
            console.error('Error fetching orphans:', err)
        }
    }

    const deleteOrphans = async (files: string[]) => {
        try {
            await instance.delete(audiosApi.deleteOrphans, {data: {files}})
            await fetchOrphans()
        } catch (err) {
            console.error('Error deleting orphans:', err)
        }
    }

    return {
        artists, loading, fetchStatus, uploadedFileName, pendingUploads, orphans, isSubmitted,
        fetchAudios, fetchOrphans, checkAudioExists, uploadTrack, saveAudios, deleteOrphans
    }
})