<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import useApiFetch from '@/composables/useApiFetch'

// Reactive variables for statuses
const registeredWithSIP = ref<boolean | null>(null) // null represents unknown
const callActive = ref<boolean | null>(null)

// Fetch status periodically
let intervalId: number | null = null

const fetchStatus = async () => {
  const { data, error } = await useApiFetch('/api/status').get().json()

  if (error.value) {
    registeredWithSIP.value = null
    callActive.value = null
  } else if (data.value) {
    registeredWithSIP.value = data.value.registeredWithSIP ?? null
    callActive.value = data.value.callActive ?? null
  }
}

// Start periodic fetch on mount
onMounted(() => {
  fetchStatus()
  intervalId = setInterval(fetchStatus, 1000)
})

// Clean up the interval on unmount
onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<template>
  <div class="p-4">
    <div class="font-bold text-lg text-center">Status</div>
    <div class="grid grid-cols-3 gap-4 items-center">
      <div class="col-span-2">Registered With SIP</div>
      <div>
        <span v-if="registeredWithSIP === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span
          v-else-if="registeredWithSIP"
          class="w-6 h-6 bg-green-500 rounded-full inline-block"
        ></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>

      <div class="col-span-2">Call Active</div>
      <div>
        <span v-if="callActive === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span v-else-if="callActive" class="w-6 h-6 bg-green-500 rounded-full inline-block"></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>
    </div>
  </div>
</template>
