<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import useApiFetch from '@/composables/useApiFetch'

// Reactive variables for statuses
const busy = ref(false)
const registeredWithSIP = ref<boolean | null>(null)
const onTheHook = ref<boolean | null>(null)
const ringing = ref<boolean | null>(null)
const callActive = ref<boolean | null>(null)

// Fetch status periodically
let intervalId: number | null = null

const fetchStatus = async () => {
  const { data, error } = await useApiFetch('/api/status').get().json()

  if (error.value) {
    busy.value = false
    registeredWithSIP.value = null
    onTheHook.value = null
    callActive.value = null
    ringing.value = null
  } else if (data.value) {
    busy.value = data.value.busy ?? false
    registeredWithSIP.value = data.value.registeredWithSIP ?? null
    onTheHook.value = data.value.onTheHook ?? null
    callActive.value = data.value.callActive ?? null
    ringing.value = data.value.ringing ?? null
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

const toggleBusy = async () => {
  busy.value = !busy.value

  const endpoint = busy.value ? '/api/busy/on' : '/api/busy/off'

  // Call the appropriate API
  const { error } = await useApiFetch(endpoint).post().json()

  if (error.value) {
    console.error(`Failed to set busy ${busy.value ? 'on' : 'off'}`, error.value.message)
    alert(`Error: Unable to set busy ${busy.value ? 'on' : 'off'}.`)
    return
  }
}
</script>

<template>
  <div class="p-4">
    <div class="flex justify-between w-full p-4 border border-purple-500 rounded">
      <div>Busy</div>
      <input
        type="checkbox"
        :checked="busy"
        @change="toggleBusy"
        class="peer sr-only opacity-0"
        id="toggle"
      />
      <label
        for="toggle"
        class="relative flex h-6 w-11 cursor-pointer items-center rounded-full bg-gray-400 px-0.5 outline-gray-400 transition-colors before:h-5 before:w-5 before:rounded-full before:bg-white before:shadow before:transition-transform before:duration-300 peer-checked:bg-green-500 peer-checked:before:translate-x-full peer-focus-visible:outline peer-focus-visible:outline-offset-2 peer-focus-visible:outline-gray-400 peer-checked:peer-focus-visible:outline-green-500"
      >
        <span class="sr-only">Enable</span>
      </label>
    </div>
    <div class="font-bold text-lg text-center mt-4">Status</div>
    <div class="grid grid-cols-3 gap-2 items-center justify-items-center py-4">
      <div class="col-span-2">Registered With SIP</div>
      <div>
        <span v-if="registeredWithSIP === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span
          v-else-if="registeredWithSIP"
          class="w-6 h-6 bg-green-500 rounded-full inline-block"
        ></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>

      <div class="col-span-2">On The Hook</div>
      <div>
        <span v-if="onTheHook === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span v-else-if="onTheHook" class="w-6 h-6 bg-green-500 rounded-full inline-block"></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>

      <div class="col-span-2">Call Active</div>
      <div>
        <span v-if="callActive === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span v-else-if="callActive" class="w-6 h-6 bg-green-500 rounded-full inline-block"></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>

      <div class="col-span-2">Ringing</div>
      <div>
        <span v-if="ringing === null" class="text-gray-500 text-xl font-bold"> X </span>
        <span v-else-if="ringing" class="w-6 h-6 bg-green-500 rounded-full inline-block"></span>
        <span v-else class="w-6 h-6 bg-red-500 rounded-full inline-block"></span>
      </div>
    </div>
  </div>
</template>
