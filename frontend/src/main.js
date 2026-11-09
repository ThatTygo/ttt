import '@fontsource/bebas-neue'
import '@fontsource-variable/inter'
import './style.css'

import { createApp } from 'vue'
import App from './App.vue'
import { auth } from './auth'
import router from './router'

auth.load().finally(() => {
  createApp(App).use(router).mount('#app')
})
