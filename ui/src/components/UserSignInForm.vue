<template>
  <form v-on:submit="submitForm">
    <h1 class="mt-5 mb-4 d-inline-block">Sign In</h1>
    or <a class="text-link" @click="$parent.action = 'sign-up'">Sign Up</a>
    <div class="form-floating mb-3">
      <input type="text" class="form-control" :class="{'is-invalid': errors.username}" id="form-username" v-model="form.username" :disabled="loading" required />
      <label for="form-username">Username</label>
      <div class="invalid-feedback d-block" v-html="errors.username" v-if="errors.username"></div>
    </div>
    <div class="form-floating mb-4">
      <input type="password" class="form-control" :class="{'is-invalid': errors.password}" id="form-password" v-model="form.password" :disabled="loading" required />
      <label for="form-password">Password</label>
      <div class="invalid-feedback d-block" v-html="errors.password" v-if="errors.password"></div>
    </div>
    <button type="submit" class="btn btn-warning float-end" :disabled="loading">Submit</button>
  </form>
</template>


<script>
import axios from 'axios'
import { Modal  } from 'bootstrap';


export default {
  methods: {
    submitForm(event) {
      event.preventDefault()
      this.loading = true
      this.errors = {}
      let form = new FormData()
      form.append('username', this.form.username)
      form.append('password', this.form.password)
      axios.post('sign-in', form).then(
        response => {
          this.$parent.updateUser({
            access_token: response.data.access_token,
            username: this.form.username,
            authorized: true
          })
          this.$parent.loadUser()
          this.form = {
            username: null,
            password: null
          }
          Modal.getInstance(
            document.getElementById('gateModal')
          ).hide()
          this.loading = false
        },
        error => {
          if (error.response.status == 422)
            error.response.data.detail.forEach(e => {
              e.loc.forEach(l => {
                if (this.form[l])
                  this.errors[l] = e.msg
              })
            })
          this.loading = false
        }
      )
    },
  },
  data() {
    return {
      loading: false,
      form: {
        username: null,
        password: null
      },
      errors: {}
    }
  },
}
</script>
