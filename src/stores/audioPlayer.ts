import {defineStore} from "pinia";
import {ref} from "vue";

export const useAudioPlayerStore = defineStore('audioPlayer', () => {
    const currentTrack = ref<HTMLAudioElement | null>(null)

    const play = (track: HTMLAudioElement) => {
        if (currentTrack.value && currentTrack.value !== track) {
            currentTrack.value.pause();
        }
        currentTrack.value = track;
        track.play();
    }

    const pause = (track: HTMLAudioElement) => {
        if (currentTrack.value === track) {
            currentTrack.value = null;
        }
        track.pause();
    }

    return { play, pause }
});