<template>
  <AddForm />
  <article class="mb-4" v-for="(topic, index) of topics.results" :key="topic.id" @click="openTopic(topic)">
    <small class="text-secondary"><b>@{{ topic.user.public_id }}</b> · {{ topic.created }}</small>
    <div class="mt-1 fs-5">{{ topic.text }}</div>
    <hr class="text-secondary" style="--bs-text-opacity: .5;" v-if="index != (topics.results.length - 1)"/>
  </article>
  <LoadingBlock v-if="loading"/>
  <ul class="pagination justify-content-center mt-4" v-else-if="!loading && topics.results.length < topics.total">
    <li class="page-item"><a class="page-link" @click="loadTopics">More...</a></li>
  </ul>
</template>

<script>
import axios from 'axios'
import AddForm from '../components/TopicAddForm.vue'
import UserBlock from '../components/UserBlock.vue'
import LoadingBlock from '../components/LoadingBlock.vue'

export default {
  name: 'TopicListView',
  methods: {
    openTopic(topic) {
      this.$router.push({
        name: 'topic_one',
        params: {
          topic_id: topic.id,
          item: JSON.stringify(topic)
        }
      })
    },
    loadTopics() {
      this.loading = !this.loading
      axios.get(`topic?page=${this.topics.page + 1}`).then(
        response => {
          response.data.results.forEach(t => {
            t.user.public_id = UserBlock.methods.decoratePublicId(t.user.public_id)
            this.topics.results.push(t)
          })
          this.topics.page = response.data.page
          this.topics.total = response.data.total
          this.loading = !this.loading
        },
      )
    }
  },
  data() {
    return {
      loading: false,
      topics: {
        page: 0,
        results: [],
        total: 0
      },
    }
  },
  mounted () {
    this.loadTopics()
  },
  components: {AddForm, LoadingBlock}
}
</script>
