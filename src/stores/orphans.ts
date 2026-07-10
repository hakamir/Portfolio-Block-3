import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import audiosApi from "@api/audios.ts";
import galleryApi from "@api/gallery.ts";

export interface OrphanAudio {
    _id: string;
    artist_title: string;
    album_title: string;
    track_title: string;
    track_number: number;
    src: string;
    tags: string[];
    deleted_at: string;
}

export interface OrphanGallery {
    _id: string;
    gallery_title: string;
    image_title: string;
    image_location: string | null;
    image_date: string | null;
    image_alt: string | null;
    image_order: number;
    src: string;
    deleted_at: string;
}

export const useOrphansStore = defineStore('orphans', () => {
    const orphanAudios = ref<OrphanAudio[]>([])
    const orphanGalleries = ref<OrphanGallery[]>([])

    // Audio
    const fetchOrphans = async () => {
        try {
            const res = await instance.get(audiosApi.getOrphans)
            orphanAudios.value = res.data
        } catch (err) {
            console.error('Error fetching orphans:', err)
        }
    }

    const deleteOrphans = async (ids: string[]) => {
        try {
            await instance.delete(audiosApi.deleteOrphans, {data: {ids}})
            await fetchOrphans()
        } catch (err) {
            console.error('Error deleting orphans:', err)
        }
    }

    const rollbackOrphans = async (ids: string[]) => {
        try {
            const res = await instance.post(audiosApi.rollbackOrphans, {ids})
            await fetchOrphans()
            return res.data as { restored: string[], failed: { id: string, title: string, error: string }[] }
        } catch (err) {
            console.error('Error rolling back orphans:', err)
            return null
        }
    }

    // Gallery
    const fetchOrphanGalleries = async () => {
        try {
            const res = await instance.get(galleryApi.getOrphans)
            orphanGalleries.value = res.data
        } catch (err) {
            console.error('Error fetching gallery orphans:', err)
        }
    }

    const deleteOrphanGalleries = async (ids: string[]) => {
        try {
            await instance.delete(galleryApi.deleteOrphans, {data: {ids}})
            await fetchOrphanGalleries()
        } catch (err) {
            console.error('Error deleting gallery orphans:', err)
        }
    }

    const rollbackOrphanGalleries = async (ids: string[]) => {
        try {
            const res = await instance.post(galleryApi.rollbackOrphans, {ids})
            await fetchOrphanGalleries()
            return res.data as { restored: string[], failed: { id: string, title: string, error: string }[] }
        } catch (err) {
            console.error('Error rolling back gallery orphans:', err)
            return null
        }
    }

    return {
        orphanAudios,
        fetchOrphans,
        deleteOrphans,
        rollbackOrphans,
        orphanGalleries,
        fetchOrphanGalleries,
        deleteOrphanGalleries,
        rollbackOrphanGalleries,
    }
})
