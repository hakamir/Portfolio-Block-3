import {defineStore} from "pinia";
import {instance} from "@api/axios.ts";
import {nextTick, ref, watch} from "vue";
import artistsApi from "@api/artists.ts";
import type {Section} from "@/types";

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

export const useArtistsStore = defineStore('artists', () => {
    const artists = ref<Artist[]>([])
    const loading = ref(false)
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')
    const isSubmitted = ref(false)
    const isDirty = ref(false)
    let isInitialized = false

    const toSlug = (str: string) => str.toLowerCase().trim().replace(/\s+/g, '_')

    watch(() => artists.value, (artists) => {
        isSubmitted.value = false
        if (isInitialized) isDirty.value = true
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

    const fetchArtists = async (section: Section) => {
        loading.value = true
        fetchStatus.value = 'loading'
        try {
            const res = await instance.get(section === "public" ? artistsApi.getArtists : artistsApi.getArtistsDashboard)
            artists.value = res.data
            await nextTick()
            isInitialized = true
            isDirty.value = false
            fetchStatus.value = 'idle'
        } catch (err) {
            fetchStatus.value = 'error'
        } finally {
            loading.value = false
        }
    }

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

    const isArtistDuplicate = (artist: Artist): boolean => {
        if (!artist.title?.trim()) return false
        return artists.value.filter(a => a.slug === artist.slug).length > 1
    }

    const isAlbumDuplicate = (album: Album, artist: Artist): boolean => {
        if (!album.title?.trim()) return false
        return artist.albums.filter(a => a.slug === album.slug).length > 1
    }

    const isTrackDuplicate = (track: Track, album: Album): boolean => {
        if (!track.title?.trim()) return false
        return album.tracks.filter(t => t.src === track.src).length > 1
    }

    const hasDuplicates = (): boolean => {
        return artists.value.some(artist =>
            isArtistDuplicate(artist) ||
            artist.albums.some(album =>
                isAlbumDuplicate(album, artist) ||
                album.tracks.some(track =>
                    isTrackDuplicate(track, album)
                )
            )
        )
    }

    const findTrackContext = (track: Track) => {
        for (const artist of artists.value) {
            const album = artist.albums.find(album => album.tracks.includes(track))
            if (album) return {artist, album}
        }
        return {artist: undefined, album: undefined}
    }

    const syncDeletedArtists = async () => {
        const existingIds = (await instance.get(artistsApi.getArtistsDashboard))
            .data.map((a: Artist) => a._id)

        const currentIds = artists.value.map(a => a._id).filter(Boolean)
        const toDelete = existingIds.filter((id: string) => !currentIds.includes(id))

        for (const id of toDelete) {
            await instance.delete(artistsApi.deleteArtist(id))
        }
    }

    const saveAudios = async () => {
        isSubmitted.value = true

        if (hasEmptyFields() || hasDuplicates()) {
            return false
        }
        fetchStatus.value = 'loading'

        // Lazy import avoids a circular module dependency at init time
        const {useAudioStore} = await import('@stores/audio')
        const audioStore = useAudioStore()
        await audioStore.uploadPendingAudios()

        const hasUploadErrors = [...audioStore.uploadStatuses.values()].includes('error')
        if (hasUploadErrors) {
            fetchStatus.value = 'error'
            return false
        }

        await syncDeletedArtists()
        await instance.put(artistsApi.updateArtists, artists.value)

        fetchStatus.value = 'idle'
        isDirty.value = false
        return true
    }

    return {
        artists,
        loading,
        fetchStatus,
        isSubmitted,
        isDirty,
        fetchArtists,
        hasEmptyFields,
        isArtistDuplicate,
        isAlbumDuplicate,
        isTrackDuplicate,
        hasDuplicates,
        findTrackContext,
        syncDeletedArtists,
        saveAudios,
    }
})
