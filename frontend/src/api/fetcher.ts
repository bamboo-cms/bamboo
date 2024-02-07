import axios, { type AxiosRequestConfig } from 'axios'
import { useSnackbar } from 'vue3-snackbar'
import type { UseAxiosOptions } from '@vueuse/integrations/useAxios'
import { useAxios } from '@vueuse/integrations/useAxios'
import { useGlobalState } from '@/lib/states'

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

client.interceptors.request.use((config) => {
  const { accessToken } = useGlobalState().value
  if (accessToken)
    config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

client.interceptors.response.use(undefined, (error) => {
  console.error('Request failed', error)
  // if (error.statusCode === 401) {
  //   const state = useGlobalState()
  //   const newToken = await getNewToken()
  //   state.value.accessToken = newToken
  //   if (newToken) {
  //     return retryWithMergedOptions({
  //       headers: {
  //         Authorization: `Bearer ${newToken}`,
  //       },
  //     })
  //   }
  // }
  return Promise.reject(error)
})

export function useFetch<T = any>(url: string, config?: AxiosRequestConfig) {
  const snackbar = useSnackbar()
  // inject instance argument to useAxios
  const options: UseAxiosOptions = {
    onError: (error: any) => {
      console.error('Request failed', error)
      snackbar.add({
        type: 'error',
        text: `request failed with ${error.response?.status || 'unknown'}: ${error.response?.data || error.message}`,
      })
    },
    immediate: true,
  }
  if (typeof config === 'undefined')
    return useAxios<T>(url, client, options)

  return useAxios<T>(url, config, client, options)
}

async function getNewToken(): Promise<string> {
  const state = useGlobalState()
  if (!state.value.refreshToken)
    return ''
  try {
    const response = await axios.post<{ access_token: string }>('auth/refresh', {
      headers: { Authorization: `Bearer ${state.value.refreshToken}` },
    })
    return response.data.access_token
  }
  catch (error) {
    console.error('Failed to refresh token', error)
    state.value.refreshToken = ''
    return ''
  }
}
