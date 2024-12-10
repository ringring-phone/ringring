<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import useApiFetch from '@/composables/useApiFetch'
import useMessage from '@/composables/useMessage'

const { showMessage } = useMessage()

// Reactive variables for form fields
const phoneNumber = ref('')
const password = ref('')
const sipIP = ref('')
const saving = ref(false)

// Fetch configuration and populate the form fields
const { data: config, error: loadingError } = await useApiFetch('/api/config').get().json()
if (loadingError.value) {
  showMessage('Error loading config', true)
}

// Watch for `config` changes and populate form fields
onMounted(() => {
  if (config.value) {
    phoneNumber.value = config.value.phoneNumber || ''
    password.value = config.value.password || ''
    sipIP.value = config.value.sipIP || ''
  }
})

// Computed property to validate the form
const valid = computed(() => {
  return (
    phoneNumber.value.trim() !== '' && password.value.trim() !== '' && sipIP.value.trim() !== ''
  )
})

// Function to save the updated configuration to the server
const saveConfig = async () => {
  const updatedConfig = {
    phoneNumber: phoneNumber.value,
    password: password.value,
    sipIP: sipIP.value,
  }

  saving.value = true

  const { data: response, error: saveError } = await useApiFetch('/api/config')
    .post(updatedConfig)
    .json()

  saving.value = false

  if (saveError.value) {
    showMessage(saveError.value.message || 'An unexpected error occurred.', true)
  } else if (response.value) {
    // Display success or error message based on response
    if (response.value.error) {
      showMessage(response.value.error, true)
    } else if (response.value.message) {
      showMessage(response.value.message)
    }
  }
}
</script>

<template>
  <div class="p-4">
    <div class="font-bold text-lg text-center">Settings</div>
    <form
      @submit.prevent="saveConfig"
      class="pt-4 grid grid-cols-2 mx-auto gap-3 items-center text-center"
    >
      <label for="phoneNumber">Phone Number</label>
      <input
        id="phoneNumber"
        type="phone"
        v-model="phoneNumber"
        placeholder="Enter phone number"
        class="bg-slate-500 px-4 py-2 rounded text-white"
        autocomplete="username"
      />
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        v-model="password"
        placeholder="Enter password"
        class="bg-slate-500 px-4 py-2 rounded text-white"
        autocomplete="current-password"
      />
      <label for="sipIP">SIP IP</label>
      <input
        id="sipIP"
        type="text"
        v-model="sipIP"
        placeholder="Enter SIP IP"
        class="bg-slate-500 px-4 py-2 rounded text-white"
      />

      <button
        type="submit"
        class="text-white rounded px-4 py-2 mt-2 col-span-2 bg-purple-500 disabled:bg-purple-300"
        :disabled="!valid || saving"
      >
        <span v-if="saving" class="spinner"></span>
        <span v-else>Save Settings</span>
      </button>
    </form>
  </div>
</template>
