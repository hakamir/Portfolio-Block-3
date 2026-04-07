<script setup lang="ts">
import {onMounted} from "vue";

onMounted(async () => {
  const res = await fetch('http://127.0.0.1:5000/messages')
  const data = await res.json()
  console.log(data)
})
</script>

<template>
  <h1>Portfolio</h1>
</template>

<style scoped>

</style>