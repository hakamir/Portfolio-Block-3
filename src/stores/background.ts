import {defineStore} from "pinia";
import {computed, ref} from "vue";
import backgroundApi from "@/api/background";
import {instance} from "@api/axios.ts";

export interface BackgroundImage {
    sm: string
    md: string
    lg: string
}

export interface BackgroundData {
    _id: string
    hero: BackgroundImage | null
    portfolio: BackgroundImage | null
    biography: BackgroundImage | null
}

const apiUrl = import.meta.env.VITE_API_URL + '/api'

const placeholdersUrl = `${apiUrl}/upload/background/placeholder`

export const PLACEHOLDERS: Record<string, BackgroundImage> = {
    hero: {
        sm: `${placeholdersUrl}/hero/hero-512.webp`,
        md: `${placeholdersUrl}/hero/hero-1024.webp`,
        lg: `${placeholdersUrl}/hero/hero-2048.webp`,
    },
    portfolio: {
        sm: `${placeholdersUrl}/portfolio/portfolio-512.webp`,
        md: `${placeholdersUrl}/portfolio/portfolio-1024.webp`,
        lg: `${placeholdersUrl}/portfolio/portfolio-2048.webp`,
    },
    biography: {
        sm: `${placeholdersUrl}/biography/biography-512.webp`,
        md: `${placeholdersUrl}/biography/biography-1024.webp`,
        lg: `${placeholdersUrl}/biography/biography-2048.webp`,
    }
}

const prefixImage = (img: BackgroundImage | null | undefined, placeholder: BackgroundImage): BackgroundImage => {
    if (!img) return placeholder
    return {
        sm: `${apiUrl}${img.sm}`,
        md: `${apiUrl}${img.md}`,
        lg: `${apiUrl}${img.lg}`,
    }
}

export const useBackgroundStore = defineStore('background', () => {
    const background = ref<BackgroundData | null>(null)
    const loading = ref<boolean>(false)
    const error = ref<boolean>(false)

    const fetchBackground = async () => {
        loading.value = true
        error.value = false
        try {
            const res = await instance.get(backgroundApi.getActiveBackground)
            background.value = res.data
        } catch {
            error.value = true
        } finally {
            loading.value = false
        }
    }

    const heroBg = computed((): BackgroundImage => prefixImage(background.value?.hero, PLACEHOLDERS.hero))

    const portfolioBg = computed((): BackgroundImage => prefixImage(background.value?.portfolio, PLACEHOLDERS.portfolio))

    const biographyBg = computed((): BackgroundImage => prefixImage(background.value?.biography, PLACEHOLDERS.biography))

    return {background, loading, error, fetchBackground, heroBg, portfolioBg, biographyBg}
})