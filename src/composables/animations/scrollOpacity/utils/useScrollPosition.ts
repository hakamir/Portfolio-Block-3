import {onBeforeUnmount, onMounted, ref} from "vue";


export default (scrollContainer: string = 'main') => {
    const scrollPosition = ref(0);
    let scrollElement: HTMLElement | null = null;

    const handleScroll = (event: Event) => {
        const target = event.target as HTMLElement;
        scrollPosition.value = target.scrollTop;
    }

    onMounted(() => {
        scrollElement = document.querySelector(scrollContainer);
        if (scrollElement) {
            scrollElement.addEventListener('scroll', handleScroll);
            scrollPosition.value = scrollElement.scrollTop;
        } else {
            console.warn('Scroll container not found');
        }
    })

    onBeforeUnmount(() => {
        if (scrollElement) {
            scrollElement.removeEventListener('scroll', handleScroll);
        }
    })

    return scrollPosition;
}