import {computed, onMounted, ref, type Ref, watch} from "vue";
import useScrollPosition from "./utils/useScrollPosition.ts";
import useOpacityCalculator from "./utils/useOpacityCalculator.ts";

export interface UseScrollOpacityOptions {
    maxScroll?: number;
    offset?: number;
    scrollContainer?: string;
}

export default (elementRef: Ref<HTMLElement | null>, options: UseScrollOpacityOptions = {}) => {
    const rgb = ref('0, 0, 0')

    const extractRGB = () => {
        if (!elementRef.value) return;
        const bgColor = window.getComputedStyle(elementRef.value).backgroundColor;
        const rgbaMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
        if (rgbaMatch) {
            rgb.value = `${rgbaMatch[1]}, ${rgbaMatch[2]}, ${rgbaMatch[3]}`
        }
    }

    const scrollPosition = useScrollPosition(options.scrollContainer ?? 'main');
    const opacity = useOpacityCalculator(
        scrollPosition,
        {maxScroll: options.maxScroll, offset: options.offset}
    );

    const backgroundColor = computed(() => {
        return `rgba(${rgb.value}, ${opacity.value})`
    })

    onMounted(() => {
        extractRGB();
    })

    watch(elementRef, () => {
        extractRGB();
    })

    return {
        scrollPosition: computed(() => scrollPosition.value),
        opacity: computed(() => opacity.value),
        rgb: computed(() => rgb.value),
        backgroundColor,
        extractRGB
    }
}