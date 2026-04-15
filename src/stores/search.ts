import {defineStore} from 'pinia'
import {ref} from 'vue'
import type {SearchEntry} from '@/composables/useSearchIndex'


export const useSearchStore = defineStore('search', () => {
    const activeFilters = ref<SearchEntry[]>([])

    /**
     * Adds `entry` to the active filters.
     * No-op if an entry with the same `id` is already present.
     */
    const addFilter = (entry: SearchEntry) => {
        if (activeFilters.value.find(f => f.id === entry.id)) return
        activeFilters.value.push(entry)
    }

    /** Removes the filter matching `id`. No-op if it does not exist. */
    const removeFilter = (id: string) => {
        activeFilters.value = activeFilters.value.filter(f => f.id !== id)
    }

    /** Removes all active filters at once. */
    const clearFilters = () => {
        activeFilters.value = []
    }

    return {activeFilters, addFilter, removeFilter, clearFilters}
})
