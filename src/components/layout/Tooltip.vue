<script setup lang="ts">
import {ref, computed} from "vue"

type Side = 'top' | 'bottom' | 'left' | 'right'
type Align = 'start' | 'center' | 'end'

interface Props {
  message: string
  icon?: Function
  iconBgColor?: string
  size?: number
  delay?: number
  side?: Side
  align?: Align
}

const {
  message,
  icon,
  iconBgColor = "bg-gray-700/50",
  size = 28,
  delay = 100,
  side = 'top',
  align = 'center'
} = defineProps<Props>()

const triggerRef = ref<HTMLElement | null>(null)
const showTooltip = ref(false)
const tooltipTop = ref(0)
const tooltipLeft = ref(0)

const updatePosition = () => {
  if (!triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()

  switch (side) {
    case 'top':
      tooltipTop.value = rect.top + window.scrollY - 8
      tooltipLeft.value = rect.left + window.scrollX + rect.width / 2
      break
    case 'bottom':
      tooltipTop.value = rect.bottom + window.scrollY + 8
      tooltipLeft.value = rect.left + window.scrollX + rect.width / 2
      break
    case 'left':
      tooltipTop.value = rect.top + window.scrollY + rect.height / 2
      tooltipLeft.value = rect.left + window.scrollX - 8
      break
    case 'right':
      tooltipTop.value = rect.top + window.scrollY + rect.height / 2
      tooltipLeft.value = rect.right + window.scrollX + 8
      break
  }
}

const onMouseEnter = () => {
  updatePosition()
  showTooltip.value = true
}

const translateClass = computed(() => {
  switch (side) {
    case 'top':
      return align === 'center' ? '-translate-x-1/2 -translate-y-full' : '-translate-y-full'
    case 'bottom':
      return align === 'center' ? '-translate-x-1/2' : ''
    case 'left':
      return align === 'center' ? '-translate-x-full -translate-y-1/2' : '-translate-x-full'
    case 'right':
      return align === 'center' ? '-translate-y-1/2' : ''
    default:
      return ''
  }
})
</script>

<template>
  <div ref="triggerRef"
       @mouseenter="onMouseEnter"
       @mouseleave="showTooltip = false"
       class="relative">
    <slot/>
  </div>

  <Teleport to="body">
    <Transition name="tooltip-fade">
      <div v-if="showTooltip"
           class="fixed z-100 pointer-events-none bg-gray-800/60 backdrop-blur-sm rounded-2xl text-white p-2 text-sm whitespace-nowrap flex items-center gap-2"
           :class="translateClass"
           :style="{ top: tooltipTop + 'px', left: tooltipLeft + 'px', transitionDelay: `${delay}ms` }">
        <component v-if="icon" :is="icon" :size="size" class="border rounded-full border-gray-300/70 p-1"
                   :class="iconBgColor"/>
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.tooltip-fade-enter-active {
  transition: opacity 0.15s ease;
}

.tooltip-fade-leave-active {
  transition: opacity 0.1s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>