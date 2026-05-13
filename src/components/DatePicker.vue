<script setup lang="ts">
import {ref, computed, onMounted, onUnmounted} from 'vue'
import {ChevronLeft, ChevronRight, Calendar} from '@lucide/vue'

defineProps<{
  isMobile?: boolean
}>()

const model = defineModel<string>({required: true})

// Native input date value (YYYY-MM-DD)
const nativeValue = computed({
  get: () => model.value ? model.value.split('T')[0] : '',
  set: (val: string) => {
    model.value = val ? `${val}T00:00:00Z` : ''
  }
})

const showPicker = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const pickerRef = ref<HTMLElement | null>(null)
const pickerTop = ref(0)
const pickerLeft = ref(0)

const displayDate = computed(() => {
  if (!model.value) return ''
  return model.value.split('T')[0].replace(/-/g, '/')
})

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth())

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December']

const updatePosition = () => {
  if (triggerRef.value) {
    const rect = triggerRef.value.getBoundingClientRect()
    pickerTop.value = rect.bottom + 4
    pickerLeft.value = rect.left
  }
}

const openPicker = () => {
  updatePosition()
  showPicker.value = !showPicker.value
}

const prevMonth = () => {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else viewMonth.value--
}

const nextMonth = () => {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else viewMonth.value++
}

const daysInMonth = computed(() => {
  const days: (number | null)[] = []
  const firstDay = new Date(viewYear.value, viewMonth.value, 1).getDay()
  const total = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  for (let i = 0; i < firstDay; i++) days.push(null)
  for (let i = 1; i <= total; i++) days.push(i)
  return days
})

const selectDate = (day: number | null) => {
  if (!day) return
  const month = String(viewMonth.value + 1).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  model.value = `${viewYear.value}-${month}-${dayStr}T00:00:00Z`
  showPicker.value = false
}

const isSelected = (day: number | null) => {
  if (!day || !model.value) return false
  const selected = new Date(model.value)
  return selected.getFullYear() === viewYear.value &&
      selected.getMonth() === viewMonth.value &&
      selected.getDate() === day
}

const handleClickOutside = (e: MouseEvent) => {
  if (
      triggerRef.value && !triggerRef.value.contains(e.target as Node) &&
      pickerRef.value && !pickerRef.value.contains(e.target as Node)
  ) {
    showPicker.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', updatePosition, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', updatePosition, true)
})
</script>

<template>
  <!-- MOBILE -->
  <input
      v-if="isMobile"
      type="date"
      v-model="nativeValue"
      class="bg-white border w-full border-gray-300 rounded-lg px-3 py-2 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-gray-400"
  />

  <!-- DESKTOP -->
  <div v-else class="relative">
    <div class="flex items-center border-l border-b border-gray-300">
      <input
          :value="displayDate"
          disabled
          placeholder="YYYY/MM/DD"
          class="bg-white px-3 py-2 w-32 focus:outline-none placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75 font-semibold"
          @click="openPicker"
      />
      <button ref="triggerRef"
              @click="openPicker"
              class="px-2 py-2 bg-gray-200/50 border-x border-gray-300 hover:bg-gray-300/50 transition group">
        <Calendar class="w-6 h-6 text-gray-600 group-hover:text-gray-800 transition"/>
      </button>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showPicker" ref="pickerRef"
             class="fixed z-50 bg-white border border-gray-300 rounded-2xl shadow-[0_0_10px_rgba(0,0,0,0.2)] overflow-hidden w-72"
             :style="{ top: pickerTop + 'px', left: pickerLeft + 'px' }">

          <div class="flex items-center justify-between mb-3 p-4 bg-gray-600 text-white">
            <button @click="prevMonth" class="p-1 hover:bg-gray-700 rounded-lg transition">
              <ChevronLeft class="w-6 h-6"/>
            </button>
            <span class="font-semibold text-sm">{{ monthNames[viewMonth] }} {{ viewYear }}</span>
            <button @click="nextMonth" class="p-1 hover:bg-gray-700 rounded-lg transition">
              <ChevronRight class="w-6 h-6"/>
            </button>
          </div>

          <div class="grid grid-cols-7 mb-1">
            <span v-for="day in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="day"
                  class="text-center text-xs text-gray-700 font-medium py-1 select-none">
              {{ day }}
            </span>
          </div>

          <div class="grid grid-cols-7 gap-1">
            <button v-for="(day, index) in daysInMonth" :key="index"
                    @click="selectDate(day)"
                    :disabled="!day"
                    class="aspect-square rounded-lg text-sm transition"
                    :class="[
                      !day ? '' : 'hover:bg-gray-100',
                      isSelected(day) ? 'bg-black text-white hover:text-black' : ''
                    ]">
              {{ day }}
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>