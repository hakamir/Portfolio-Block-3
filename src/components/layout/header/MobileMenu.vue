<script setup lang="ts">
import {computed, onMounted, onUnmounted, ref, watch} from "vue";
import {LogOut} from "@lucide/vue";
import {useAuthStore} from "@stores";
import {useRoute} from "vue-router";

const props = defineProps<{ color: "white" | "black" }>()
const bgColor = computed(() => props.color === "black" ? "bg-white" : "bg-black")
const store = useAuthStore()
const open = ref(false)
const route = useRoute()
const menuRef = ref<HTMLElement | null>(null)

watch(() => route.fullPath, () => {
  open.value = false
})

const handleClickOutside = (event: MouseEvent) => {
  if (!menuRef.value) return;
  if (!menuRef.value.contains(event.target as Node)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const toggleMenu = () => {
  open.value = !open.value
}
</script>

<template>
  <div class="block lg:hidden ms-auto" ref="menuRef">
    <div class="block lg:hidden z-20 relative">
      <button @click="toggleMenu" class="menu-button" type="button" aria-label="Menu button">
        <span class="line" :class="`bg-${props.color}`"></span>
        <span class="line" :class="`bg-${props.color}`"></span>
        <span class="line" :class="`bg-${props.color}`"></span>
      </button>
    </div>
    <div v-if="open"
         class="absolute top-0 right-0 px-4 pt-16 pb-8 border-gray-500/50 rounded-bl-2xl border-l border-b"
         :class="`${bgColor}`">
      <ul class="flex flex-col gap-4">
        <li>
          <RouterLink to="/" active-class="selected" class="nav-item font-unbounded">
            HOME
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/portfolio" active-class="selected" class="nav-item font-unbounded">
            PORTFOLIO
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/contact" active-class="selected" class="nav-item font-unbounded">
            CONTACT
          </RouterLink>
        </li>
        <li v-if="!store.isAuthenticated()">
          <RouterLink to="/login" active-class="selected" class="nav-item font-unbounded">
            LOGIN
          </RouterLink>
        </li>
        <li v-if="store.isAuthenticated()">
          <RouterLink
              to="/dashboard"
              active-class="selected"
              class="nav-item">
            DASHBOARD
          </RouterLink>
        </li>
        <li v-if="store.isAuthenticated()">
          <button
              @click="store.logout"
              class="nav-item">
            <LogOut/>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>

</style>