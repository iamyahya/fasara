<template>
  <LoadingBlock v-if="loadingTopic"/>
  <section v-else>
    <small class="text-secondary"><b>@{{ topic.user.public_id }}</b> · {{ topic.created }}</small>
    <p class="fs-5 mt-1 mb-3">{{ topic.text }}</p>
    <hr class="text-secondary mt-3 mb-4" style="--bs-text-opacity: .5;"/>
    <h5 class="text-muted d-inline-block mb-4 mt-2">{{ responses.total }} Response(s)</h5>
    <button class="btn btn-warning btn-sm ms-3" data-bs-toggle="modal" data-bs-target="#responseModal" v-if="$root.books.length">Add</button>
  </section>
  <article v-for="response in responses.results" :key="response.id" class="mb-4 pb-2">
    <small class="text-muted"><b>@{{ response.user.public_id }}{{ response.doubles ? ' +' + response.doubles : '' }}</b> · {{ response.created }}</small>
    <div v-for="text in response.texts" :key="text.number" :class="{ 'text-end arabic': text.structure.book.language == 'ar' }">
      <p class="mb-2 text-muted" :class="{ 'small': text.structure.book.language != 'ar' }">{{
        text.type == 'ayat' ?
        text.structure.surah.name :
        text.structure.chapter.name
      }}</p>
      <section v-if="text.structure.book.language == 'ar'" class="fs-0 mb-3">
        <span class="text-muted" v-if="text.meta" v-html="text.meta.narrated"></span><span  :class="{'text-success': text.type == 'ayat', 'text-primary': text.type == 'hadith'}">{{ text.content }}</span>
      </section>
      <section v-else class="small">
        <span class="text-muted" v-if="text.meta && text.meta.narrated" v-html="text.meta.narrated + ': '"></span><span v-html="text.content"></span>
      </section>
    </div>
    <hr class="text-secondary mt-3 mb-0" style="--bs-text-opacity: .5;" />
    <div class="position-relative">
      <div class="bg-white ps-1 pe-1 text-muted small text-capitalize position-absolute top-50 start-50 translate-middle" style="margin-top: -1px">
        {{ response.texts[0].structure.book.title }}
        <small>
          · 
          {{
            response.texts[0].type == 'ayat' ?
            response.texts[0].structure.surah.number :
            response.texts[0].structure.chapter.number
          }}
          · 
          {{ response.texts[0].number }}
          {{ response.texts[0].meta && response.texts[0].meta.grade ? '· ' + response.texts[0].meta.grade: '' }} 
        </small>
      </div>
    </div>
  </article>
  <ul class="pagination justify-content-center mt-4" v-if="responses.total_ < responses.total">
    <li class="page-item"><a class="page-link" @click="loadResponses">More...</a></li>
  </ul>
  <LoadingBlock v-if="loadingResponses" />
  <AddForm v-else-if="$root.user.authorized"/>
</template>

<script>
import axios from 'axios'
import AddForm from '../components/ResponseAddForm.vue'
import UserBlock from '../components/UserBlock.vue'
import LoadingBlock from '../components/LoadingBlock.vue'

export default {
  methods: {
    sendComplaint() {
      console.log(this.topic.id)
    },
    loadTopic() {
      if ('item' in this.$route.params) {
        this.topic = JSON.parse(this.$route.params.item)
        this.topic.user.public_id = UserBlock.methods.decoratePublicId(this.topic.user.public_id)
        this.topic.complaints.forEach(c => {
          c.user.public_id = UserBlock.methods.decoratePublicId(c.user.public_id)
        })
      } else {
        this.loadingTopic = !this.loadingTopic
        axios.get('topic/' + this.$route.params.topic_id).then(
          response => {
            this.topic = response.data
            this.topic.user.public_id = UserBlock.methods.decoratePublicId(this.topic.user.public_id)
            this.topic.complaints.forEach(c => {
              c.user.public_id = UserBlock.methods.decoratePublicId(c.user.public_id)
            })
            this.loadingTopic = !this.loadingTopic
          }
        )
      }
    },
    filterTexts(texts) {
      let includes = texts.map(t => t.structure.book.language).includes(this.$root.user.language)
      texts.forEach((t, i) => {
        t.content = t.content.replace(/[\uFDFA]/g, '<span class="arabic">ﷺ</span>')
        if (t.meta && t.meta.narrated)
          t.meta.narrated = t.meta.narrated.replace(/[\uFDFA]/g, '<span class="arabic">ﷺ</span>')
        if (t.structure.book.language == 'ar') {
          /* do nothing */
        } else if (this.$root.user.language == 'ar') {
          if (t.structure.book.language != 'en')
            texts.splice(i, 1)
        } else if (includes) {
          if (t.structure.book.language != this.$root.user.language)
            texts.splice(i, 1)
        } else {
          if (t.structure.book.language != 'en')
            texts.splice(i, 1)
        }
      })
    },
    loadResponses() {
      this.loadingResponses = !this.loadingResponses
      const url = 'response/' + this.$route.params.topic_id + 
                  '?page=' + (this.responses.page + 1)
      axios.get(url).then(
        response => {
          response.data.results.forEach(r => {
            r.user.public_id = UserBlock.methods.decoratePublicId(r.user.public_id)
            this.filterTexts(r.texts)
            this.responses.results.push(r)
          })
          this.responses.page = response.data.page
          this.responses.total = response.data.total
          this.responses.total_ = this.responses.results.length
          this.responses.results.forEach(r => {
            this.responses.total_ += r.doubles
          })
          this.loadingResponses = !this.loadingResponses
        },
      )
    }
  },
  data() {
    return {
      loadingTopic: false,
      loadingResponses: false,
      topic: {
        user: {},
        complaints: []
      },
      responses: {
        page: 0,
        results: [],
        total: 0,
        total_: 0
      }
    }
  },
  mounted () {
    this.loadTopic()
    this.loadResponses()
  },
  components: {AddForm, LoadingBlock}
}
</script>

<style>
.arabic {
  font-family: 'Noto Sans Arabic', sans-serif;
}
</style>
