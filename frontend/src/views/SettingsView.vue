<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import useApiFetch from '@/composables/useApiFetch'

// Reactive variables for form fields
const phoneNumber = ref('')
const password = ref('')
const sipIP = ref('')
const saving = ref(false)
const statusMessage = ref('')
const isError = ref(false)
const showMessage = ref(false)

// Function to set the status message
const setStatusMessage = (message: string, error = false) => {
  statusMessage.value = message
  isError.value = error

  // Show the message and fade it out after 5 seconds
  showMessage.value = true
  setTimeout(() => {
    showMessage.value = false
    statusMessage.value = ''
    isError.value = false
  }, 3000)
}

// Fetch configuration and populate the form fields
const { data: config, error: loadingError } = await useApiFetch('/api/config').get().json()
if (loadingError.value) {
  setStatusMessage('Error loading config', true)
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
    setStatusMessage(saveError.value.message || 'An unexpected error occurred.', true)
  } else if (response.value) {
    // Display success or error message based on response
    if (response.value.error) {
      setStatusMessage(response.value.error, true)
    } else if (response.value.message) {
      setStatusMessage(response.value.message)
    }
  }
}
</script>

<template>
  <div class="p-4">
    <div class="font-bold text-lg text-center">Settings</div>
    <div
      v-if="showMessage"
      :class="[
        'transition-opacity duration-5000 ease-in-out fixed top-4 left-1/2 transform -translate-x-1/2 p-4 rounded-lg shadow-lg max-w-md',
        isError ? 'bg-red-300 text-black' : 'bg-green-300 text-black',
        'animate-fade',
      ]"
    >
      {{ statusMessage }}
    </div>
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
        class="text-white rounded px-4 py-2 col-span-2 bg-purple-500 disabled:bg-purple-300"
        :disabled="!valid || saving"
      >
        <span v-if="saving" class="spinner"></span>
        <span v-else>Save Settings</span>
      </button>
    </form>
  </div>
</template>
