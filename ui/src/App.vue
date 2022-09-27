<template>
  <nav class="navbar bg-light">
    <div class="container-fluid">
      <span class="navbar-brand text-success" @click="goHome">Fasara</span>
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link" data-bs-toggle="modal" @click="syncBooks" data-bs-target="#gateModal" v-if="!user.authorized"><span class="text-muted text-opacity-75">Login</span> <font-awesome-icon icon="fa-solid fa-arrow-right-to-bracket" /></a>
          <a class="nav-link" @click="logout" v-else><b>@{{ user.public_id }}</b> <font-awesome-icon class="ms-1" icon="fa-solid fa-arrow-right-from-bracket" /></a>
        </li>
      </ul>
    </div>
  </nav>
  <div class="container-fluid mt-3">
    <Invite v-if="$root.user.authorized"/>
    <router-view v-slot="{ Component  }">
      <keep-alive  :include="/TopicListView/">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
  <User v-if="!$root.user.authorized"/>
</template>


<script>
/*
TODO: Complaint add form
TODO: Number of Complaints in TopicOne

TODO: Textarea height auto for TopicAddForm
TODO: Update one topic
TODO: Save or publish toggler for TopicAddForm
TODO: Style for list `more` button TopicList and TopicOne (responses)
TODO: Search form for topic list
TODO: Change default language for user
TODO: Explain users number in response
TODO: In ResponseAddForm show success and failure after add
TODO: In ResponseAddForm book placeholders
TODO: My topics list

- TODO: New Invite notification
_ TODO: In responses list translated text should be based on user language
- TODO: In ResponseAddForm show text based on user language
- TODO: SignUp form
- TODO: LoginForm to modal window
- TODO: Logout button as list item
- TODO: Interface to english
- TODO: Loading animation
- TODO: Load fonts from /public
*/

import User from './components/UserBlock.vue'
import Invite from './components/InviteBlock.vue'

export default {
  methods: {
    goHome() {
      /* if (this.$route.name == 'TopicListViev') */
      /*   return */
      /* this.$router.go(-1) */
      this.$router.push({ name: 'topic_list' })
    },
    syncUser() {
      this.user = User.methods.readUser()
    },
    logout() {
      localStorage.removeItem('user')
      this.syncUser()
      this.books = []
    },
  },
  data() {
    return {
      // Fill books in './components/ResponseAddForm.vue'
      books: [],
      user: User.methods.readUser(),
    }
  },
  components: { User, Invite },
}
</script>


<style>
/* arabic */
@font-face {
  font-family: 'Noto Sans Arabic';
  font-style: normal;
  font-weight: 300;
  font-stretch: 100%;
  src: url(../public/fonts/Noto Sans Arabic.woff2) format('woff2');
  unicode-range: U+0600-06FF, U+200C-200E, U+2010-2011, U+204F, U+2E41, U+FB50-FDFF, U+FE80-FEFC, U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;

}
.navbar-brand,
.navbar-brand:hover {
  cursor: pointer;
}
</style>
