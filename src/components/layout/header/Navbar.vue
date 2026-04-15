<script setup lang="ts">
import {vTilt} from '@directives/tilt'
import {LogOut} from "@lucide/vue";
import {useAuthStore} from "@stores";

const store = useAuthStore()


</script>

<template>
  <div class="hidden md:block ms-auto">
    <nav>
      <ul class="flex space-x-12 text-lg font-bold">
        <li>
          <RouterLink
              to="/"
              active-class="selected"
              class="nav-item"
              v-tilt
          >
            HOME
          </RouterLink>
        </li>
        <li>
          <RouterLink
              to="/portfolio"
              active-class="selected"
              class="nav-item"
              v-tilt
          >
            PORTFOLIO
          </RouterLink>
        </li>
        <li>
          <RouterLink
              to="/contact"
              active-class="selected"
              class="nav-item"
              v-tilt
          >
            CONTACT
          </RouterLink>
        </li>
        <li v-if="store.isAuthenticated()">
          <RouterLink
              to="/dashboard"
              active-class="selected"
              class="nav-item"
              v-tilt>
            DASHBOARD
          </RouterLink>
        </li>
        <li v-if="store.isAuthenticated()">
          <button
              @click="store.logout"
              class="nav-item"
              v-tilt>
            <LogOut/>
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<style scoped>
</style>