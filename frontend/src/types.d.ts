declare module 'vue3-snackbar' {
  import type { Plugin } from 'vue'

  export const SnackbarService: Plugin

  interface ISnackbarOptions {
    text: string
    type?: 'success' | 'error' | 'warning' | 'info'
    title?: string
    dismissable?: boolean
  }

  export const useSnackbar: () => {
    add: (props: ISnackbarOptions) => void
  }

  export const Vue3Snackbar: any
}
