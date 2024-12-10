import { ref } from 'vue'

// Shared state
const message = ref('Configuration Saved Successfully')
const isError = ref(false)
const show = ref(false)

const showMessage = (msg: string, error: boolean = false): void => {
  message.value = msg
  isError.value = error
  show.value = true

  // Automatically hide the message after 3 seconds
  setTimeout(() => {
    show.value = false
  }, 2000)
}

// Singleton pattern
export default function useMessage() {
  return {
    message,
    isError,
    show,
    showMessage,
  }
}
