import {defineStore} from "pinia";
import {nextTick, ref, watch} from "vue";
import {instance} from "@api/axios.ts";
import galleryApi from "@api/gallery.ts";


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
    const orphans = ref<string[]>([])
    const isDirty = ref(false)
    let isInitialized = false
    const isSubmitted = ref(false);

    const fetchGalleries = async () => {
        const res = await instance.get(galleryApi.getGalleries)
        galleries.value = res.data
        galleries.value.sort((a, b) => a.order - b.order)
        galleries.value.forEach(gallery => {
            gallery.images.sort((a, b) => a.order - b.order)
        })
        await nextTick()
        isInitialized = true
        isDirty.value = false
    }

    const toSlug = (str: string) => str.toLowerCase().trim().replace(/\s+/g, '_')

    watch(() => galleries.value, (galleries) => {
        isSubmitted.value = false;
        if (isInitialized) isDirty.value = true
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
        // Mark form as submitted and set loading state
        isSubmitted.value = true;

        // Abort if validation fails
        if (hasEmptyFields() || hasDuplicates()) {
            return false
        }
        fetchStatus.value = 'loading'

        // Upload pending galleries
        for (const [image, file] of pendingUploads.value.entries()) {
            const gallery = galleries.value.find(g => g.images.includes(image))
            if (!gallery) continue
            uploadedFileName.value = pendingUploads.value.get(image)?.name;
            // Get random name prefix by gallery slug
            image.src = `${gallery.slug}_${crypto.randomUUID()}.webp`

            const formData = new FormData()
            formData.append('file', file)
            formData.append('gallerySlug', gallery.slug)
            formData.append('imageSrc', image.src)

            await instance.post(galleryApi.uploadImage, formData)
        }
        pendingUploads.value.clear()
        uploadedFileName.value = undefined;
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
        fetchStatus.value = 'idle'
        isDirty.value = false
        return true
    }

    const fetchOrphans = async () => {
        try {
            const res = await instance.get(galleryApi.getOrphans)
            orphans.value = res.data
        } catch (err) {
            console.error('Error fetching orphans:', err)
        }
    }

    const deleteOrphans = async (files: string[]) => {
        try {
            await instance.delete(galleryApi.deleteOrphans, {data: {files}})
            await fetchOrphans()
        } catch (err) {
            console.error('Error deleting orphans:', err)
        }
    }

    const isGalleryDuplicate = (gallery: Gallery): boolean => {
        if (!gallery.title?.trim()) return false // Avoid UI to trigger duplication check if empty
        return galleries.value.filter(a => a.slug === gallery.slug).length > 1
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
        galleries, orphans, pendingUploads, fetchStatus, uploadedFileName, isDirty, isSubmitted,
        fetchGalleries, saveGalleries, checkImageExists, fetchOrphans, deleteOrphans, isGalleryDuplicate
    }
});