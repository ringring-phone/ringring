<script setup lang="ts">
import { ref } from 'vue';

const visible = ref(false)
</script>

<template>
  <header>
    <nav class="bg-purple-500 px-4 py-2.5 w-full grid grid-cols-3 items-center">
      <!-- Hamburger -->
      <button data-collapse-toggle="mobile-menu" type="button" class="text-white inline-flex items-center p-2 ml-1"
        aria-controls="mobile-menu" aria-expanded="false" @click="visible = !visible">
        <FontAwesomeIcon v-if="!visible" :icon="['fas', 'bars']" class="text-white" />
        <FontAwesomeIcon v-if="visible" :icon="['fas', 'xmark']" class="text-white" />
      </button>

      <!-- Title -->
      <div class="text-white text-center">RingRing</div>

      <!-- Placeholder -->
      <div></div>

      <!-- Menu -->
      <div v-if="visible" class="col-span-3 w-full mt-50px px-4 py-2.5text-white" id="mobile-menu">
        <ul class="flex flex-col mt-4 font-medium">
          <li>
            <RouterLink to="/"
              class="block py-2 pr-4 pl-3 text-gray-700 border-gray-100 hover:bg-gray-50 dark:border-gray-700"
              activeClass="text-white rounded bg-slate-700" @click="visible = false">
              Home
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/log"
              class="block py-2 pr-4 pl-3 text-gray-700 border-gray-100 hover:bg-gray-50 dark:border-gray-700"
              activeClass="text-white rounded bg-slate-700" @click="visible = false">
              Log
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/settings"
              class="block py-2 pr-4 pl-3 text-gray-700 border-gray-100 hover:bg-gray-50 dark:border-gray-700"
              activeClass="text-white rounded bg-slate-700" @click="visible = false">
              Settings
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/tests"
              class="block py-2 pr-4 pl-3 text-gray-700 border-gray-100 hover:bg-gray-50 dark:border-gray-700"
              activeClass="text-white rounded bg-slate-700" @click="visible = false">
              Tests
            </RouterLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>
