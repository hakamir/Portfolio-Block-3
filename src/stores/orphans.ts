import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import audiosApi from "@api/audios.ts";

export interface OrphanMetadata {
    artist: string;
    album: string;
    title: string;
    track_number: number;
}

export interface OrphanAudioRaw {
    file: string;
    metadata: OrphanMetadata | null;
}

export const useOrphansStore = defineStore('orphans', () => {
    const orphans = ref<OrphanAudioRaw[]>([])

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

    const rollbackOrphans = async (files: string[]) => {
        try {
            const res = await instance.post(audiosApi.rollbackOrphans, {files})
            await fetchOrphans()
            return res.data as { restored: string[], failed: { file: string, error: string }[] }
        } catch (err) {
            console.error('Error rolling back orphans:', err)
            return null;
        }
    }

    return {
        orphans,
        fetchOrphans,
        deleteOrphans,
        rollbackOrphans
    }
})