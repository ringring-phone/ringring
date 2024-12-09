<script setup lang="ts">
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
</script>

<template>
  <div class="flex flex-col min-h-screen bg-slate-800 text-white">
    <Header />
    <Suspense>
      <template #default>
        <RouterView />
      </template>
      <template #fallback>
        <div>Loading...</div>
      </template>
    </Suspense>
  </div>
</template>
