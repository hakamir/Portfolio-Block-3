import {defineStore} from "pinia";
import {ref, watch} from "vue";
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

    const pendingUploads = ref<Map<Image, File>>(new Map())

    const fetchGalleries = async () => {
        const res = await instance.get(galleryApi.getGalleries)
        galleries.value = res.data
        galleries.value.sort((a, b) => a.order - b.order)
        galleries.value.forEach(gallery => {
            gallery.images.sort((a, b) => a.order - b.order)
        })
    }

    const getNextSrc = async (gallerySlug: string): Promise<string> => {
        const res = await instance.get(`/gallery/next-src?gallerySlug=${gallerySlug}`)
        return res.data.src
    }

    const toSlug = (str: string) => str.toLowerCase().trim().replace(/\s+/g, '_')

    watch(() => galleries.value, (galleries) => {
        galleries.forEach(gallery => {
            gallery.slug = toSlug(gallery.title)
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
        try {
            // Upload pending images
            for (const [image, file] of pendingUploads.value.entries()) {
                const gallery = galleries.value.find(g => g.images.includes(image))
                if (!gallery) continue

                // Get next available src
                const src = await getNextSrc(gallery.slug)
                image.src = src

                const formData = new FormData()
                formData.append('file', file)
                formData.append('gallerySlug', gallery.slug)
                formData.append('imageSrc', src)
                await instance.post(galleryApi.uploadImage, formData)
            }
            pendingUploads.value.clear()

            // Delete galleries that no longer exist
            const existingIds = (await instance.get(galleryApi.getGalleries)).data
                .map((g: Gallery) => g._id)
            const currentIds = galleries.value.map(g => g._id).filter(id => id)
            const toDelete = existingIds.filter((id: string) => !currentIds.includes(id))
            for (const id of toDelete) {
                await instance.delete(galleryApi.deleteGallery(id))
            }

            // Save galleries
            await instance.put(galleryApi.updateGalleries, galleries.value)
        } catch (err) {
            console.error('Error saving galleries:', err)
            throw err
        }
    }

    return {galleries, fetchGalleries, saveGalleries, pendingUploads, checkImageExists}
});