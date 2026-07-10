import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import audiosApi from "@api/audios.ts";

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

export const useOrphansStore = defineStore('orphans', () => {
    const orphans = ref<OrphanAudio[]>([])

    const fetchOrphans = async () => {
        try {
            const res = await instance.get(audiosApi.getOrphans)
            orphans.value = res.data
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

    return {
        orphans,
        fetchOrphans,
        deleteOrphans,
        rollbackOrphans
    }
})
