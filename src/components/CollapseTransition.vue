<!-- CollapseTransition.vue -->
<script setup lang="ts">
defineProps<{
  show: boolean,
  customClass?: string
  delay?: number
}>()

const onEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = '0'
  element.offsetHeight
  element.style.height = element.scrollHeight + 'px'
}

const onAfterEnter = (el: Element) => {
  (el as HTMLElement).style.height = 'auto'
}

const onLeave = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = element.scrollHeight + 'px'
  element.offsetHeight
  element.style.height = '0'
}
</script>

<template>
  <Transition @enter="onEnter" @after-enter="onAfterEnter" @leave="onLeave">
    <div v-if="show" class="overflow-hidden" :class="customClass" :style="`transition: height ${delay || 300}ms ease-in-out`">
      <slot/>
    </div>
  </Transition>
</template>