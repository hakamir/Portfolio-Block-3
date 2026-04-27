<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import {Send, TriangleAlert, LoaderCircle} from "@lucide/vue";
import {useContactStore} from "@stores";
import {storeToRefs} from "pinia";

const store = useContactStore()
const {formData, status} = storeToRefs(store)
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <div class="flex flex-1">
      <section class="pt-28 pb-16 md:pt-48 container mx-auto px-8 md:px-32">
        <div class="md:grid md:grid-cols-2 p-8 gap-16 border border-gray-300 rounded-xl bg-gray-100">
          <div class="pb-8">
            <h1 class="text-4xl font-unbounded">Get in touch!</h1>
            <p class="pt-4">Feel free to reach out to me for any inquiries, collaborations, or just to say hello.
              I'm always open to new opportunities and excited to hear from you!</p>
          </div>
          <form v-if="status !== 'submitted'" id="form-contact" class="flex flex-col"
                @submit.prevent="store.sendMessage">
            <div class="flex items-center border rounded-t-xl bg-white border-gray-300 group focus-within:ring-2 focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <label for="name" class="block font-unbounded px-4 w-24 group-focus-within:-translate-x-1 group-focus-within:text-black/80 transition">Name</label>
              <input id="name" type="text" v-model="formData.name" class="w-full h-10 outline-none" required>
            </div>
            <div
                class="flex items-center border-x bg-white border-gray-300 group focus-within:ring-2 focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <label for="email" class="block font-unbounded px-4 w-24 group-focus-within:-translate-x-1 group-focus-within:text-black/80 transition">Email</label>
              <input id="email" type="email" name="email" v-model="formData.email"
                     class="w-full h-10 outline-none" required>
            </div>
            <div class="flex flex-col border border-gray-300 bg-white group focus-within:ring-2 focus-within:bg-white/70 ring-inset ring-black/50 transition">
              <textarea id="message" placeholder="Your message..." v-model="formData.message"
                        class="px-4 py-2 w-full min-h-25 outline-none placeholder:font-unbounded focus:placeholder:opacity-50 placeholder:text-sm placeholder:font-extralight"
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