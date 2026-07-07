import {defineStore} from "pinia";
import {nextTick, ref, watch} from "vue";
import {instance} from "@api/axios.ts";
import biographyApi from "@api/biography.ts";

export const useBiographyStore = defineStore("biography", () => {
    const biography = ref()
    const isDirty = ref(false)
    let isInitialized = false

    watch(() => biography.value, () => {
        if (isInitialized) isDirty.value = true
    }, {deep: true})

    const fetchBiography = async () => {
        const res = await instance.get(biographyApi.getBiography)
        const {updatedAt, ...rest} = res.data.biography
        biography.value = rest
        await nextTick()
        isInitialized = true
        isDirty.value = false
    }

    const fetchBiographyDashboard = async () => {
        const res = await instance.get(biographyApi.getBiographyDashboard)
        const {updatedAt, ...rest} = res.data.biography
        biography.value = rest
        await nextTick()
        isInitialized = true
        isDirty.value = false
    }

    const updateBiography = async () => {
        await instance.put(biographyApi.updateBiography, biography.value)
        isDirty.value = false
    }

    return {biography, isDirty, fetchBiography, fetchBiographyDashboard, updateBiography}
})