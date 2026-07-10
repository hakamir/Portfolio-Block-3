import {defineStore} from "pinia";
import {instance} from "@api/axios.ts";
import {ref} from "vue";
import audiosApi from "@api/audios.ts";
import type {TrackUploadStatus} from "@/types";
import type {Track} from "@stores/artists";

export const useAudioStore = defineStore('audio', () => {
    const uploadStatuses = ref<Map<Track, TrackUploadStatus>>(new Map())
    const pendingUploads = ref<Map<Track, File>>(new Map())

    const checkAudioExists = async (src: string | undefined, track?: Track) => {
        if (!src) return false
        try {
            await instance.head(src)
            if (track) uploadStatuses.value.set(track, 'uploaded')
            return true
        } catch {
            return false
        }
    }

    const removeTrackState = (track: Track) => {
        pendingUploads.value.delete(track)
        uploadStatuses.value.delete(track)
    }

    const addPendingUpload = (track: Track, file: File) => {
        pendingUploads.value.set(track, file)
        uploadStatuses.value.set(track, 'pending')
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

    const uploadPendingAudios = async () => {
        // Lazy import avoids a circular module dependency at init time
        const {useArtistsStore} = await import('@stores/artists')
        const artistsStore = useArtistsStore()

        const results = await Promise.allSettled(
            [...pendingUploads.value.entries()].map(async ([track, file]) => {
                const {artist, album} = artistsStore.findTrackContext(track)
                if (!artist || !album || !track.src) return

                const formData = new FormData()
                formData.append('file', file)
                formData.append('artistSlug', artist.slug)
                formData.append('albumSlug', album.slug)
                formData.append('trackSrc', track.src)
                formData.append('artistTitle', artist.title)
                formData.append('albumTitle', album.title)
                formData.append('trackTitle', track.title)
                formData.append('trackNumber', track.trackNumber.toString())
                formData.append('trackTags', track.tags.join(","))

                uploadStatuses.value.set(track, 'uploading')
                try {
                    await instance.post(audiosApi.uploadAudio, formData)
                    uploadStatuses.value.set(track, 'uploaded')
                } catch (err) {
                    uploadStatuses.value.set(track, 'error')
                }
            })
        )

        results.forEach((result) => {
            if (result.status === 'rejected') {
                console.error('Upload failed', result.reason)
            }
        })
        pendingUploads.value.clear()
    }

    return {
        uploadStatuses,
        pendingUploads,
        checkAudioExists,
        removeTrackState,
        addPendingUpload,
        uploadTrack,
        uploadPendingAudios,
    }
})
