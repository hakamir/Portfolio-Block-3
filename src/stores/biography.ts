import {defineStore} from "pinia";
import {nextTick, ref, watch} from "vue";
import {instance} from "@api/axios.ts";
import biographyApi from "@api/biography.ts";
import type {Section} from "@/types";

export const useBiographyStore = defineStore("biography", () => {
    const biography = ref()
    const isDirty = ref(false)
    let isInitialized = false

    watch(() => biography.value, () => {
        if (isInitialized) isDirty.value = true
    }, {deep: true})

    const fetchBiography = async (section: Section = 'public') => {
        biography.value = null
        const res = await instance.get(section === 'public' ? biographyApi.getBiography : biographyApi.getBiographyDashboard)
        const {updatedAt, ...rest} = res.data.biography
        biography.value = rest
        await nextTick()
        isInitialized = true
        isDirty.value = false
    }

    const fetchBiographyByUser = async (id: string) => {
        return await instance.get(biographyApi.getBiographyByUser(id))
    }

    const updateBiography = async () => {
        await instance.put(biographyApi.updateBiography, biography.value)
        isDirty.value = false
    }

    const createBiography = async (id: string) => {
        await instance.post(biographyApi.createBiography, {
            user_id: id,
            title: '',
            sections: [],
        })
    }

    const deleteBiography = async (id: string) => {
        await instance.delete(biographyApi.deleteBiography(id))
    }

    return {biography, isDirty, fetchBiography, fetchBiographyByUser, updateBiography, createBiography, deleteBiography}
})