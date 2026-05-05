<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import {Send, TriangleAlert, LoaderCircle} from "@lucide/vue";
import {useContactStore} from "@stores";
import {storeToRefs} from "pinia";
import {onMounted, onUnmounted, ref} from "vue";

const store = useContactStore()
const {formData, status} = storeToRefs(store)

const isMobile = ref(window.innerWidth < 768)

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
})

</script>

<template>
  <div class="flex flex-col min-h-screen">
    <div class="flex flex-1">
      <section class="pt-28 pb-16 md:pt-48 xl:container xl:mx-auto px-6 lg:px-32">
        <div class="md:grid md:grid-cols-2 md:p-8 gap-16 md:border border-gray-300 rounded-xl md:bg-gray-100">
          <div class="pb-8">
            <h1 class="text-3xl md:text-4xl font-unbounded">Get in touch!</h1>
            <p class="pt-4">Feel free to reach out to me for any inquiries, collaborations, or just to say hello.
              I'm always open to new opportunities and excited to hear from you!</p>
          </div>
          <form v-if="status !== 'submitted'" id="form-contact" class="flex flex-col"
                @submit.prevent="store.sendMessage">
            <div class="relative flex items-center border rounded-t-xl bg-white h-14 border-gray-300 group focus-within:inset-shadow-[0_0_5px_rgba(0,0,0,0.5)] focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <label v-if="!isMobile || !formData.name.trim()" for="name" class="block font-unbounded px-4 w-24 group-focus-within:-translate-x-1 group-focus-within:text-black/0 md:group-focus-within:text-black/80 transition select-none">Name</label>
              <input id="name" type="text" v-model="formData.name" class="absolute md:relative w-full h-12 outline-none px-4" required>
            </div>
            <div
                class="relative flex items-center border-x bg-white h-14 border-gray-300 group focus-within:inset-shadow-[0_0_5px_rgba(0,0,0,0.5)] focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <label v-if="!isMobile || !formData.email.trim()" for="email" class="block font-unbounded px-4 w-24 group-focus-within:-translate-x-1 group-focus-within:text-black/0 md:group-focus-within:text-black/80 transition select-none">Email</label>
              <input id="email" type="email" name="email" v-model="formData.email" class="absolute md:relative w-full h-12 outline-none px-4" required>
            </div>
            <div class="flex flex-col border border-gray-300 bg-white group focus-within:inset-shadow-[0_0_5px_rgba(0,0,0,0.5)] focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <textarea id="message" placeholder="Your message..." v-model="formData.message"
                        class="px-4 py-2 w-full min-h-70 outline-none placeholder:font-unbounded focus:placeholder:opacity-50 placeholder:text-sm placeholder:font-extralight"
                        required autocomplete="off"></textarea>
            </div>
            <div class="flex flex-col justify-end">
              <button id="submit-button" type="submit"
                      class="bg-black text-white px-6 py-3 outline-none focus:ring-2 focus:shadow-[0_0_10px_rgba(0,0,0,1)] ring-black font-unbounded rounded-b-xl transition-all duration-300 hover:bg-neutral-700">
                <span v-if="status !== 'loading'"
                      class="flex items-center justify-center gap-2">
                  <Send/>
                  <span>Send Message</span>
                </span>
                <LoaderCircle v-else class="animate-spin"/>
              </button>
              <div v-if="status === 'error'" class="flex justify-center mt-2">
                <span class="px-3 py-2 rounded-xl text-red-500 bg-red-100 text-sm flex items-center">
                  <TriangleAlert class="inline-block mr-2"/>
                  An error occurred while sending your message. Please try again later.
                </span>
              </div>
            </div>
          </form>
          <div v-else>
            <h2 class="text-2xl font-unbounded">Thank you for your message!</h2>
            <p class="pt-4">I will get back to you soon.</p>
            <button
                @click="store.resetForm"
                id="new-message"
                class="bg-black text-white px-6 py-3 font-unbounded rounded transition-all duration-300 hover:bg-neutral-700 mt-4">
              New message
            </button>
          </div>
        </div>
      </section>
    </div>
    <Footer customClass="bg-black"/>
  </div>
</template>

<style scoped>

</style>