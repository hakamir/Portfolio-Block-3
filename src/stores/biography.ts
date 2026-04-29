import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import biographyApi from "@api/biography.ts";

export const useBiographyStore = defineStore("biography", () => {
    const biography = ref()

    const fetchBiography = async () => {
        const res = await instance.get(biographyApi.getBiography)
        const {updatedAt, ...rest} = res.data.biography
        biography.value = rest
    }

    const updateBiography = async () => {
        await instance.put(biographyApi.updateBiography, biography.value)
        biography.value = biography.value
    }

    return {biography, fetchBiography, updateBiography}
})