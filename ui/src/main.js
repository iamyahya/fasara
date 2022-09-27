import { createApp } from 'vue'
import axios from 'axios'
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'

import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import { library  } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon  } from '@fortawesome/vue-fontawesome'
import {
  faArrowRightFromBracket,
  faArrowRightToBracket,
  faAngleLeft
} from '@fortawesome/free-solid-svg-icons'

library.add(faArrowRightFromBracket)
library.add(faArrowRightToBracket)
library.add(faAngleLeft)

axios.defaults.baseURL = `http://${process.env.VUE_APP_API_URL}/`

const app = createApp(App).use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')

// import mitt from 'mitt'
// app.config.globalProperties.emitter = mitt()
// this.emitter.emit('sign-in')
