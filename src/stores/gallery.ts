import {defineStore} from "pinia";
import {nextTick, ref, watch} from "vue";
import {instance} from "@api/axios.ts";
import galleryApi from "@api/gallery.ts";
import type {Section} from "@/types";


export interface Image {
    src: string
    alt: string
    title: string
    location: string
    date: string
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
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')
    const uploadedFileName = ref<string | undefined>(undefined);
    const isDirty = ref(false)
    let isInitialized = false
    const isSubmitted = ref(false);

    const fetchGalleries = async (section: Section = 'public') => {
        const res = await instance.get(section === 'public' ? galleryApi.getGalleries : galleryApi.getGalleriesDashboard)
        galleries.value = res.data
        galleries.value.sort((a, b) => a.order - b.order)
        galleries.value.forEach(gallery => {
            gallery.images.sort((a, b) => a.order - b.order)
        })
        await nextTick()
        isInitialized = true
        isDirty.value = false
    }

    watch(() => galleries.value, (galleries) => {
        isSubmitted.value = false;
        if (isInitialized) isDirty.value = true
        galleries.forEach(gallery => {
            gallery.images.forEach(image => {
                const year = image.date ? new Date(image.date).getFullYear() : ''
                image.alt = [image.title, image.location, year].filter(Boolean).join(', ')
            })
        })
    }, {deep: true})

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
        isSubmitted.value = true

        if (hasEmptyFields() || hasDuplicates()) {
            return false
        }
        fetchStatus.value = 'loading'

        // Delete galleries removed from the UI
        const existingIds = (await instance.get(galleryApi.getGalleriesDashboard)).data
            .map((g: Gallery) => g._id)
        const currentIds = galleries.value.map(g => g._id).filter(id => id)
        const toDelete = existingIds.filter((id: string) => !currentIds.includes(id))
        for (const id of toDelete) {
            await instance.delete(galleryApi.deleteGallery(id))
        }

        // PUT metadata — server assigns UUID slugs for new galleries and srcs for new images
        const saved: Gallery[] = (await instance.put(galleryApi.updateGalleries, galleries.value)).data

        // Patch local galleries in-place to preserve Map<Image, File> references
        galleries.value.forEach((gallery, gi) => {
            const serverGallery = saved[gi]
            gallery._id = serverGallery._id
            gallery.slug = serverGallery.slug
            gallery.images.forEach((image, ii) => {
                image.src = serverGallery.images[ii].src
            })
        })

        // Upload pending images using server-assigned slugs and srcs
        for (const [image, file] of pendingUploads.value.entries()) {
            const gallery = galleries.value.find(g => g.images.includes(image))
            if (!gallery) continue
            uploadedFileName.value = file.name

            const formData = new FormData()
            formData.append('file', file)
            formData.append('gallerySlug', gallery.slug)
            formData.append('imageSrc', image.src)

            await instance.post(galleryApi.uploadImage, formData)
        }
        pendingUploads.value.clear()
        uploadedFileName.value = undefined

        fetchStatus.value = 'idle'
        isDirty.value = false
        return true
    }

    const isGalleryDuplicate = (gallery: Gallery): boolean => {
        if (!gallery.title?.trim()) return false
        const normalized = gallery.title.trim().toLowerCase()
        return galleries.value.filter(g => g.title.trim().toLowerCase() === normalized).length > 1
    }

    const hasDuplicates = (): boolean => {
        return galleries.value.some(gallery => isGalleryDuplicate(gallery))
    }

    const hasEmptyFields = (): boolean => {
        return galleries.value.some(gallery =>
            !gallery.title?.trim() ||
            gallery.images.some(image =>
                !image.title?.trim() ||
                !image.location?.trim()
            )
        )
    }

    return {
        galleries, pendingUploads, fetchStatus, uploadedFileName, isDirty, isSubmitted,
        fetchGalleries, saveGalleries, checkImageExists, isGalleryDuplicate
    }
});