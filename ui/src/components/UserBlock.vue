<template>
  <div class="modal fade" id="gateModal" tabindex="-1" aria-labelledby="gateModalLabel" aria-hidden="true">
    <div class="modal-fullscreen-sm-down modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn btn-light text-muted" data-bs-dismiss="modal" aria-label="Close">
            <font-awesome-icon icon="fa-solid fa-angle-left" />
          </button>
        </div>
        <div class="modal-body" style="padding-left: 12px; padding-right: 12px;">
          <div class="container-fluid py-0 px-0 mb-3">
            <SignInForm v-if="action == 'sign-in'" />
            <SignUpForm v-else />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import SignInForm from './UserSignInForm.vue'
import SignUpForm from './UserSignUpForm.vue'


export default {
  methods: {
    decoratePublicId(value) {
      return `${value.slice(0, 4)}...${value.slice(-3)}`
    },
    syncToken() {
      if (!this.$root.user.authorized)
        return
      let date = new Date();
      date.setDate(date.getDate() - 5);
      if (date < this.$root.user.last_sync)
        return
      axios.get('token', {'headers': this.authHeaders()}).then(
        response => {
          this.updateUser({
            access_token: response.data.access_token,
            last_sync: new Date().toISOString()
          })
        },
        () => this.logout()
      )
    },
    authHeaders() {
      let user = this.readUser()
      if (user.access_token != null)
        return {
          Authorization: 'Bearer ' + user.access_token
        }
    },
    loadUser() {
      if (this.$root.user.access_token == null)
        return
      axios.get('user', {headers: this.authHeaders()}).then(
        response => {
          let data = response.data
          this.updateUser({
            public_id: this.decoratePublicId(data.public_id),
          })
        },
        () => this.logout()
      )
    },
    readUser() {
      let language = navigator.userLanguage ||
                     navigator.language
      if (localStorage.user == null)
        return {
          language: language.slice(0, 2),
          authorized: false
        }
      let result = JSON.parse(localStorage.user)
      if (result.last_sync != null) {
        result.last_sync = new Date(result.last_sync)
      }
      return result
    },
    updateUser(data) {
      for (const [key, value] of Object.entries(data))
        this.$root.user[key] = value
      localStorage.setItem('user', JSON.stringify(this.$root.user))
    },
  },
  data() {
    return {
      action: 'sign-in',
      form: {
        username: null,
        password: null
      },
      errors: {}
    }
  },
  mounted() {
    this.loadUser()
    setInterval(this.syncToken.bind(this), 1000 * 60)
  },
  components: { SignInForm, SignUpForm }
}
</script>

