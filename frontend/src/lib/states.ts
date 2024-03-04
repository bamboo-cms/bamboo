import { createGlobalState, useStorage } from '@vueuse/core'
import { ref } from 'vue'
import type { ICurrentUser } from '@/schema'

const initialState = {
  accessToken: '',
  refreshToken: '',
}

export const useGlobalState = createGlobalState(() => useStorage('bamboo-state', initialState))

const currentUser = ref<ICurrentUser | undefined>(undefined)

export function useCurrentUser() {
  return {
    currentUser,
    setCurrentUser: (user?: ICurrentUser) => {
      currentUser.value = user
    },
  }
}
