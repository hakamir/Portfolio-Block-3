<script setup lang="ts">
import { vTilt } from '../../../directives/tilt'
</script>

<template>
  <div class="hidden md:block ms-auto">
    <nav>
      <ul class="flex space-x-12 text-lg font-bold">
        <li>
          <RouterLink
            to="/"
            active-class="selected"
            class="nav-item font-unbounded"
            v-tilt
          >
            HOME
          </RouterLink>
        </li>
        <li>
          <RouterLink
            to="/portfolio"
            active-class="selected"
            class="nav-item font-unbounded"
            v-tilt
          >
            PORTFOLIO
          </RouterLink>
        </li>
        <li>
          <RouterLink
            to="/contact"
            active-class="selected"
            class="nav-item font-unbounded"
            v-tilt
          >
            CONTACT
          </RouterLink>
        </li>
      </ul>
    </nav>
  </div>
</template>

<style scoped>
</style>