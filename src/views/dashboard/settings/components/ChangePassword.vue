<script setup lang="ts">
import {ref, computed, onMounted} from 'vue'
import {Eye, EyeOff, KeyRound, Check, X} from '@lucide/vue'
import {useAuthStore} from "@stores";
import {storeToRefs} from "pinia";

const currentPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')

const showCurrent = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)


// Reactive password validation rules (length, character requirements, difference from current, confirmation match)
const rules = computed(() => ({
  minLength: newPwd.value.length >= 12,
  hasLower: /[a-z]/.test(newPwd.value),
  hasUpper: /[A-Z]/.test(newPwd.value),
  hasNumber: /\d/.test(newPwd.value),
  hasSpecial: /[^a-zA-Z0-9\s]/.test(newPwd.value),
  notSame: newPwd.value !== currentPwd.value,
  matches: newPwd.value === confirmPwd.value && confirmPwd.value !== '',
}))

// Aggregate validation state: true only if all rules pass
const isValid = computed(() => Object.values(rules.value).every(Boolean))

const authStore = useAuthStore()
const {status} = storeToRefs(authStore)

// Reset auth status when component mounts
onMounted(async () => {
  status.value = 'idle'
})

// Submit password change, handle loading/success/error states, and reset form on success
const handleSubmit = async () => {
  if (!isValid.value) return
  await authStore.changePassword(currentPwd.value, newPwd.value)
  currentPwd.value = ''
  newPwd.value = ''
  confirmPwd.value = ''
}
</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6 grid md:grid-cols-2">
    <div class="mb-6 flex flex-col justify-between">
      <div>
        <h2 class="text-2xl font-semibold">Change password</h2>
        <p class="text-sm text-gray-500 mt-1">Update your account password.</p>
      </div>
      <!-- Rules -->
      <div v-if="newPwd.length > 0" class="flex flex-col gap-1">
        <div v-for="(valid, rule) in rules" :key="rule"
             class="md:flex hidden items-center gap-2 text-md opacity-70 ml-12"
             :class="valid ? 'text-lime-700' : 'text-red-700'">
          <Check v-if="valid" class="w-5 h-5"/>
          <X v-else class="w-5 h-5"/>
          <span class="text-sm"
          >{{
              rule === 'minLength' ? 'At least 12 characters' :
                  rule === 'hasLower' ? 'One lowercase letter' :
                      rule === 'hasUpper' ? 'One uppercase letter' :
                          rule === 'hasNumber' ? 'One number' :
                              rule === 'hasSpecial' ? 'One special character' :
                                  rule === 'notSame' ? 'Different from current password' :
                                      'Passwords match'
            }}</span>
        </div>
      </div>
    </div>

    <div class="flex flex-col gap-4 max-w-md">

      <!-- Current password -->
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Current password</label>
        <div class="flex items-center border border-gray-300 rounded-xl bg-white overflow-hidden"
             :class="status === 'invalid' ? 'border-red-400' : ''">
          <input :type="showCurrent ? 'text' : 'password'"
                 v-model="currentPwd"
                 placeholder="••••••••"
                 class="flex-1 px-4 py-2 text-sm focus:outline-none bg-transparent"/>
          <button @click="showCurrent = !showCurrent" class="px-3 text-gray-400 hover:text-gray-600 transition"
                  tabindex="-1">
            <Eye v-if="!showCurrent" :size="16"/>
            <EyeOff v-else :size="16"/>
          </button>
        </div>
        <p v-if="status === 'invalid'" class="text-xs text-red-500">Incorrect current password.</p>
      </div>

      <!-- New password -->
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">New password</label>
        <div class="flex items-center border border-gray-300 rounded-xl bg-white overflow-hidden">
          <input :type="showNew ? 'text' : 'password'"
                 v-model="newPwd"
                 placeholder="••••••••"
                 class="flex-1 px-4 py-2 text-sm focus:outline-none bg-transparent"/>
          <button @click="showNew = !showNew" class="px-3 text-gray-400 hover:text-gray-600 transition" tabindex="-1">
            <Eye v-if="!showNew" :size="16"/>
            <EyeOff v-else :size="16"/>
          </button>
        </div>
      </div>

      <!-- Confirm password -->
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Confirm new password</label>
        <div class="flex items-center border border-gray-300 rounded-xl bg-white overflow-hidden"
             :class="confirmPwd.length > 0 && !rules.matches ? 'border-red-400' : ''">
          <input :type="showConfirm ? 'text' : 'password'"
                 v-model="confirmPwd"
                 placeholder="••••••••"
                 class="flex-1 px-4 py-2 text-sm focus:outline-none bg-transparent"/>
          <button @click="showConfirm = !showConfirm" class="px-3 text-gray-400 hover:text-gray-600 transition"
                  tabindex="-1">
            <Eye v-if="!showConfirm" :size="16"/>
            <EyeOff v-else :size="16"/>
          </button>
        </div>
      </div>

      <!-- Submit -->
      <button @click="handleSubmit"
              :disabled="!isValid || status === 'loading'"
              class="flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition mt-2"
              :class="isValid ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-200 text-gray-400 cursor-not-allowed'">
        <KeyRound :size="16"/>
        {{ status === 'loading' ? 'Updating...' : 'Update password' }}
      </button>

      <!-- Success -->
      <div v-if="status === 'success'"
           class="flex items-center justify-center gap-2 text-sm text-lime-600 bg-lime-50 border border-lime-200 rounded-xl px-4 py-2">
        <Check class="w-5 h-5"/>
        Password updated successfully.
      </div>

      <!-- Error -->
      <div v-if="status === 'error'"
           class="flex items-center justify-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2">
        <X class="w-5 h-5"/>
        An error occurred. Please try again.
      </div>

    </div>
    <div v-if="newPwd.length > 0" class="flex md:hidden flex-col gap-1 mt-4">
      <div v-for="(valid, rule) in rules" :key="rule"
           class="flex items-center gap-2 text-md opacity-70"
           :class="valid ? 'text-lime-700' : 'text-red-700'">
        <Check v-if="valid" class="w-5 h-5"/>
        <X v-else class="w-5 h-5"/>
        <span class="text-sm"
        >{{
            rule === 'minLength' ? 'At least 12 characters' :
                rule === 'hasLower' ? 'One lowercase letter' :
                    rule === 'hasUpper' ? 'One uppercase letter' :
                        rule === 'hasNumber' ? 'One number' :
                            rule === 'hasSpecial' ? 'One special character' :
                                rule === 'notSame' ? 'Different from current password' :
                                    'Passwords match'
          }}</span>
      </div>
    </div>
  </div>
</template>