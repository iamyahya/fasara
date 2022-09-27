<template>
  <div class="alert alert-info mb-4" v-if="code">
    <p>Send the code to invite your friend!</p>
    <hr />
    {{ code }}
  </div>
</template>
<script>
import axios from 'axios'
import User from '../components/UserBlock.vue'

export default {
  methods: {
    loadInvites() {
      axios.get(
        'user/invite',
        {'headers': User.methods.authHeaders()}
      ).then(
        response => {
          response.data.results.forEach(i => {
            if (!i.used)
              this.code = i.code
          })
        },
        error => {
          console.log(error)
        }
      )
    }
  },
  data() {
    return {
      code: null
    }
  },
  mounted() {
    this.loadInvites()
  }
}
</script>
