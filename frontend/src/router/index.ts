import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LogView from '../views/LogView.vue'
import SettingsView from '../views/SettingsView.vue'
import TestsView from '../views/TestsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/log',
      name: 'log',
      component: LogView,
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
    },
    {
      path: '/tests',
      name: 'tests',
      component: TestsView,
    }
  ],
})

export default router
