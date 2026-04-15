<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import {TriangleAlert, LoaderCircle} from "@lucide/vue";
import {useContactStore} from "@stores";
import {storeToRefs} from "pinia";

const store = useContactStore()
const { formData, status } = storeToRefs(store)
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <div class="flex flex-1">
      <section class="pt-28 pb-16 md:pt-48 container mx-auto px-8 md:px-32">
        <h1 class="text-4xl font-bold font-unbounded">Contact</h1>
        <div class="md:grid md:grid-cols-2 pt-8 gap-16">
          <div class="pb-8">
            <h2 class="text-2xl font-unbounded">Get in touch!</h2>
            <p class="pt-4">Feel free to reach out to me for any inquiries, collaborations, or just to say hello.
              I'm always open to new opportunities and excited to hear from you!</p>
          </div>
          <form v-if="status !== 'submitted'" id="form-contact" class="flex flex-col gap-4" @submit.prevent="store.sendMessage">
            <div>
              <label for="name" class="block text-lg font-bold mb-2">Name</label>
              <input id="name" type="text" placeholder="Name" v-model="formData.name"
                     class="border border-gray-300 rounded px-4 py-2 w-full" required>
            </div>
            <div>
              <label for="email" class="block text-lg font-bold mb-2">Email</label>
              <input id="email" type="email" placeholder="Email" v-model="formData.email"
                     class="border border-gray-300 rounded px-4 py-2 w-full" required>
            </div>
            <div>
              <label for="message" class="block text-lg font-bold mb-2">Message</label>
              <textarea id="message" placeholder="Message" v-model="formData.message"
                        class="border border-gray-300 rounded px-4 py-2 w-full" required></textarea>
            </div>
            <div class="flex flex-col justify-end">
              <button id="submit-button" type="submit"
                      class="bg-black text-white px-6 py-3 font-unbounded rounded transition-all duration-300 hover:bg-neutral-700 flex items-center justify-center">
                <span v-if="status !== 'loading'">Send Message</span>
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