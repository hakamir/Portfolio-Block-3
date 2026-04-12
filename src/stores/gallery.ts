import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import galleryApi from "@api/gallery.ts";

export interface Image {
    src: string
    alt: string
    title: string
    location: string
    date: Date
    order: number
}

export interface Gallery {
    _id: string
    title: string
    slug: string
    order: number
    images: Image[]
}

export const useGalleriesStore = defineStore('galleries', () => {
    const galleries = ref<Gallery[]>([])

    const fetchGalleries = async () => {
        const res = await instance.get(galleryApi.getGalleries)
        galleries.value = res.data
    }

    return {galleries, fetchGalleries}
});