<template>
  <form v-on:submit="submitForm" v-if="$root.user.authorized" class="form-floating">
    <textarea style="height:100%; border-color: #e9ecef" class="form-control mb-3" v-model="form.text" v-on:update:modelValue="onChangeFormText" :disabled="loading" required />
    <label for="floatingTextarea">Topic text</label>
    <small class="float-start text-muted mt-2 ps-2">Allowed symbols: {{ 128 - form.text.length }}</small>
    <div class="d-flex justify-content-end">
      <button type="submit" class="btn btn-warning" :class="{'opacity-25': submitButton()}" :disabled="submitButton()">Add</button>
    </div>
    <hr class="text-secondary text-opacity-50" />
  </form>
</template>

<style>
textarea {
  line-height: 1.2;
  font-weight: 500;
  font-size: calc(1.3rem + .6vw) !important;
}
</style>

<script>
import axios from 'axios'
import User from '../components/UserBlock.vue'

export default {
  methods: {
    onChangeFormText(value) {
      if (value.length > 128)
        this.form.text = this.form.text.slice(0, 128)
    },
    submitButton() {
      if (this.form.text.trim().length == 0)
        return true
      if (this.loading)
        return true
      return false
    },
    submitForm(event) {
      this.loading = true
      event.preventDefault()
      axios.post(
        'topic',
        {
          'text': this.form.text,
          'status': 2
        },
        {
          'headers': User.methods.authHeaders()
        }
      ).then(
        response => {
          let t = response.data
          t.user.public_id = User.methods.decoratePublicId(t.user.public_id) 
          this.$parent.topics.results = [
            t, ...this.$parent.topics.results
          ]
          this.$parent.topics.total += 1
          this.form.text = ''
          this.loading = false
        },
        error => {
          console.log(error)
        }
      )
    },
  },
  data() {
    return {
      loading: false,
      form: {
        text: ''
      }
    }
  },
}
</script>

