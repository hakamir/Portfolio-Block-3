import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import biographyApi from "@api/biography.ts";

export const useBiographyStore = defineStore("biography", () => {
    const biography = ref()

    const fetchBiography = async () => {
        const res = await instance.get(biographyApi.getBiography)
        biography.value = res.data.biography
    }

    return {biography, fetchBiography}
})