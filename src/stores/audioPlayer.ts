import {defineStore} from "pinia";
import {ref} from "vue";

export interface TrackMeta {
    title: string
    subtitle: string
    src: string
}

export const useAudioPlayerStore = defineStore('audioPlayer', () => {
    const currentTrack = ref<HTMLAudioElement | null>(null)
    const isPlaying = ref(false)
    const currentMeta = ref<TrackMeta | null>(null)

    const onPauseOrEnd = () => {
        isPlaying.value = false
    }

    const play = (track: HTMLAudioElement, meta: TrackMeta) => {
        if (currentTrack.value && currentTrack.value !== track) {
            currentTrack.value.removeEventListener('pause', onPauseOrEnd)
            currentTrack.value.removeEventListener('ended', onPauseOrEnd)
            currentTrack.value.pause()
        }
        track.removeEventListener('pause', onPauseOrEnd)
        track.removeEventListener('ended', onPauseOrEnd)
        track.addEventListener('pause', onPauseOrEnd)
        track.addEventListener('ended', onPauseOrEnd)
        currentTrack.value = track
        currentMeta.value = meta
        track.play()
        isPlaying.value = true
    }

    const pause = (track: HTMLAudioElement) => {
        track.pause()
        if (currentTrack.value === track) {
            isPlaying.value = false
        }
    }

    return {play, pause, currentTrack, isPlaying, currentMeta}
});