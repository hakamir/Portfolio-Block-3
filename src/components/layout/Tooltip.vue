<script setup lang="ts">

import {computed} from "vue";

type Side = 'top' | 'bottom' | 'left' | 'right'
type Align = 'start' | 'center' | 'end'

interface Props {
  message: string
  icon?: object
  iconBgColor?: string
  size?: number
  groupRef?: string
  delay?: number
  side?: Side
  align?: Align
}

const {message, icon, iconBgColor = "bg-gray-700/50", size = 28, groupRef, delay = 500, side = 'top', align = 'center'} = defineProps<Props>()

const sideBase = {
  top: 'bottom-full mb-2',
  bottom: 'top-full mt-2',
  left: 'right-full mr-2',
  right: 'left-full ml-2'
} as const

const alignMap = {
  top: {
    start: 'left-0',
    center: 'left-1/2 -translate-x-1/2',
    end: 'right-0'
  },
  bottom: {
    start: 'left-0',
    center: 'left-1/2 -translate-x-1/2',
    end: 'right-0'
  },
  left: {
    start: 'top-0',
    center: 'top-1/2 -translate-y-1/2',
    end: 'bottom-0'
  },
  right: {
    start: 'top-0',
    center: 'top-1/2 -translate-y-1/2',
    end: 'bottom-0'
  }
} as const

const positionClass = computed(() => {
  const s = side ?? 'top'
  const a = align ?? 'center'

  return [
    sideBase[s],
    alignMap[s][a]
  ]
})

</script>

<template>
  <div
      :class="[
    'absolute z-100 pointer-events-none',
    positionClass,
    'bg-gray-800/60 backdrop-blur-sm rounded-2xl text-white p-2',
    'text-sm transition-opacity whitespace-nowrap flex items-center gap-2',
    `delay-[${delay}]`,
    'opacity-0',
    {
      [`group-hover/${groupRef}:opacity-100`]: groupRef,
      'group-hover:opacity-100': !groupRef
    }
  ]"
  >
    <component :is="icon" :size="size" class="border rounded-full border-gray-300/70 p-1"
               :class="iconBgColor"/>
    {{ message }}
  </div>
</template>
