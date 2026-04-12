import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import galleryApi from "@api/gallery.ts";

export interface DateTime {
    $date: string
}

export interface Image {
    src: string
    alt: string
    title: string
    location: string
    date: DateTime
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

    const pendingUploads = ref<Map<Image, File>>(new Map())

    const fetchGalleries = async () => {
        const res = await instance.get(galleryApi.getGalleries)
        galleries.value = res.data
        galleries.value.sort((a, b) => a.order - b.order)
        galleries.value.forEach(gallery => {
            gallery.images.sort((a, b) => a.order - b.order)
        })
        console.log(galleries.value)
    }

    const checkImageExists = async (src: string | undefined): Promise<boolean> => {
        if (!src) return false
        try {
            await fetch(src, {method: 'HEAD'})
            return true
        } catch {
            return false
        }
    }

    const saveGalleries = async () => {
        console.log('Saving galleries:', galleries.value)
    }

    return {galleries, fetchGalleries, saveGalleries, pendingUploads, checkImageExists}
});