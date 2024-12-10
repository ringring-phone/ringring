<script setup lang="ts">
import { ref } from 'vue'
import useApiFetch from '@/composables/useApiFetch'

// Reactive state to track ringing status
const isRinging = ref(false)

const { data, error } = await useApiFetch('/api/ringer/status').get().json()
if (data.value?.status !== undefined) {
  isRinging.value = data.value.status
}

// Function to handle button click
const toggleRinging = async () => {
  const endpoint = isRinging.value ? '/api/ringer/stop' : '/api/ringer/start'

  // Call the appropriate API
  const { error } = await useApiFetch(endpoint).post().json()

  if (error.value) {
    console.error(`Failed to ${isRinging.value ? 'stop' : 'start'} ringing:`, error.value.message)
    alert(`Error: Unable to ${isRinging.value ? 'stop' : 'start'} ringing.`)
    return
  }

  // Toggle the state
  isRinging.value = !isRinging.value
}
</script>

<template>
  <div class="p-4">
    <div class="font-bold text-lg text-center">Tests</div>
    <div class="grid grid-cols-3 gap-2 items-center justify-items-center py-4">
      <div class="col-span-2">Ringer</div>
      <button
        @click="toggleRinging"
        class="px-6 py-2 text-white rounded-lg"
        :class="isRinging ? 'bg-red-500 hover:bg-red-700' : 'bg-green-500 hover:bg-green-700'"
      >
        {{ isRinging ? 'Stop' : 'Start' }}
      </button>
    </div>
  </div>
</template>
