import { createApp } from 'vue'
import { SnackbarService } from 'vue3-snackbar'
import App from './App.vue'
import './style.css'
import 'vue3-snackbar/styles'

createApp(App).use(SnackbarService).mount('#app')
