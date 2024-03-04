import { createApp } from 'vue'
import { SnackbarService } from 'vue3-snackbar'
import App from './App.vue'
import './style.css'
import 'vue3-snackbar/styles'
import router from './routes'

const app = createApp(App)

app.use(router)
app.use(SnackbarService)

app.mount('#app')
