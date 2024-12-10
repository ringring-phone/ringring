<script setup lang="ts">
import useMessage from '@/composables/useMessage'

const { message, isError, show } = useMessage()
</script>

<template>
  <div
    v-if="show"
    :class="[
      'animate-fade text-center fixed top-4 left-1/2 transform -translate-x-1/2 p-4 rounded-lg shadow-lg max-w-sm w-full',
      isError ? 'bg-red-300 text-black' : 'bg-green-300 text-black',
    ]"
  >
    {{ message }}
  </div>
</template>
