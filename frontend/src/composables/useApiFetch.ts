import { createFetch } from '@vueuse/core'

// Dynamically determine the base URL using the host IP and a specified port
const API_BASE_URL = `http://${window.location.hostname}:8080`

const useApiFetch = createFetch({
  baseUrl: API_BASE_URL,
})

export default useApiFetch
