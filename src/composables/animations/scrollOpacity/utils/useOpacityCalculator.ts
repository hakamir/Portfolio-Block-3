import {computed, type Ref} from "vue";

export interface OpacityOptions {
    maxScroll?: number;
    offset?: number;
}

export default (scrollPosition: Ref<number>, options: OpacityOptions = {}) => {
    const maxScroll = options.maxScroll ?? 0;
    const offset = options.offset ?? 0;

    const opacity = computed(() => {
        return Math.min(Math.max((scrollPosition.value - offset) / maxScroll, 0), 1)
    })

    return opacity;
}