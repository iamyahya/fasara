<template>
  {{ syncBooks() }}
  <div class="modal fade" id="responseModal" tabindex="-1" aria-labelledby="responseModalLabel" aria-hidden="true">
    <div class="modal-fullscreen-sm-down modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn btn-light text-muted" data-bs-dismiss="modal" aria-label="Close">
            <font-awesome-icon icon="fa-solid fa-angle-left" />
          </button>
        </div>
        <div class="modal-body" style="padding-left: 12px; padding-right: 12px;">
          <div class="container-fluid py-0 px-0 mb-3" style="overflow-x: scroll">
            <div class="d-flex flex-row flex-nowrap">
              <div
                class="card card-body car-body text-capitalize"
                v-for="book in $root.books" :key="book.order"
                :class="{
                  'opacity-25': form.book.title && form.book.title != book.title
                }"
                @click="selectBook(book)">
                <br /> {{ book.title }}
              </div>
            </div>
          </div>
          <div class="container-fluid py-0 px-0 mb-3" style="overflow-x: scroll; overflow-y: hidden" dir="auto">
            <div class="d-flex flex-row flex-nowrap" :class="{'arabic': form.book.language == 'ar', 'small': form.book.language != 'ar'}">
              <div style="min-width: 85%;" v-for="column in form.book.chapters" :key="column">
                <div
                  class="chapter-item"
                  v-for="chapter in column" :key="chapter.number"
                  :class="{'opacity-25': form.chapter.number && form.chapter.number != chapter.number}"
                  @click="selectChapter(chapter)">
                  <small class="text-muted" style="">{{ chapter.number }}</small> <span>{{ chapter.name }}</span>
                </div>
              </div>
            </div>
          </div>
          <hr class="text-secondary mt-3 mb-3 opacity-25" v-if="form.chapter.number" />
          <div dir="auto" :class="{'arabic text-end': form.book.language == 'ar',}">
            <div
              class="text-item"
              v-for="text in texts"
              :key="text.number"
              :class="{
                'opacity-25': form.text.number && text.number != form.text.number,
                'text-ayat': text.type == 'ayat',
                'text-hadith': text.type == 'hadith'
              }"
              @click="selectText(text)">
              <p class="fs-0 mb-0 mt-2"
                :class="{
                  'd-inline': text.type == 'ayat',
                  'text-success': text.number == form.text.number && text.type == 'ayat',
                  'text-primary': text.number == form.text.number && text.type != 'ayat',
                }">
                <span class="text-muted" v-if="text.meta && text.meta.narrated">{{ text.meta.narrated }}{{ form.book.language == 'ar' ? '' : ': ' }}</span>
                <span v-html="text.content"></span> 
              </p><small v-if="text.type == 'ayat'" v-html="text.number"></small>
              <div class="position-relative pb-2 mb-4" v-if="text.type == 'hadith'">
                <hr class="text-secondary mt-3 mb-0" style="--bs-text-opacity:0.5;">
                <div class="bg-white ps-1 pe-1 text-muted small text-capitalize position-absolute top-50 start-50 translate-middle" style="margin-top: -1px;">
                  <div style="position: relative; top: -3px">
                     <small>· {{ text.number }} ·</small>
                     <small style="background: #fff; position: absolute; margin-top: 2px; margin-left: 5px; min-width: 45px;" class="text-muted" v-if="text.meta && text.meta.grade"> · {{ text.meta.grade }} · </small>
                  </div>
                </div>
              </div>
              <button @click="submitForm" class="btn btn-sm btn-warning" v-if="form.text.number && text.number == form.text.number">＋</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import User from '../components/UserBlock.vue'

export default {
  methods: {
    selectBook(book) {
      if (book.title == this.form.book.title)
        return
      this.form.book = book
      this.form.chapter = {}
      this.form.text = {}
      this.texts = []
    },
    selectChapter(chapter) {
      if (chapter.name == this.form.chapter.name)
        return
      this.form.chapter = chapter
      this.form.text = {}
      let prefix = ''
      if (chapter.type == 'chapter')
        prefix = 'hadith/'
      axios.get(`${prefix}${this.form.book.title}:${this.form.book.language}/${this.form.chapter.number}`).then(
        response => {
          response.data.results.forEach((text, i) => {
            response.data.results[i].content = text.content.replace(/[\uFDFA]/g, '<span class="arabic">ﷺ</span>')
          })
          this.texts = response.data.results
        }
      )
    },
    selectText(text) {
      if (text.number == this.form.text.number)
        this.form.text = {}
      else
        this.form.text = text
    },
    submitForm() {
      if (this.form.text.number == null)
        return
      axios.post(
        `response/${this.$route.params.topic_id}`,
        {
          book_title: this.form.book.title,
          chapter_number: this.form.chapter.number,
          text_number: this.form.text.number
        },
        {'headers': User.methods.authHeaders()}
      ).then(
        response => {
          this.$parent.responses.total += 1
          this.$parent.responses.total_ += 1
          let t1 = response.data.texts[0]
          let i1 = -1
          for (const [i2, r2] of Object.entries(this.$parent.responses.results)) {
            let t2 = r2.texts[0]
            if (
              t1.number == t2.number &&
              t1.structure.book.title == t2.structure.book.title
            ) {
              if (
                (
                  t1.type == 'ayat' &&
                  t1.structure.surah.number == t2.structure.surah.number
                ) || (
                  t1.type == 'hadith' &&
                  t1.structure.chapter.number == t2.structure.chapter.number
                )
              ) {
                i1 = i2; break
              }
            }
          }
          if (this.$parent.responses.results[i1]) {
            this.$parent.responses.results[i1].doubles += 1
          } else {
            response.data.user.public_id = User.methods.decoratePublicId(response.data.user.public_id)
            this.$parent.filterTexts(response.data.texts)
            this.$parent.responses.results = [
              response.data, ...this.$parent.responses.results
            ]
          }
        }
      )
    },
    createChaptersColumn(column) {
      let rows = 0
      column.forEach(chapter => {
        if (chapter.name.length > 41)
          rows += 2
        else
          rows += 1
      })
      return rows >= 13
    },
    addBook(book, prefix='') {
      let language = 'ar'
      if (book.languages.includes(this.$root.user.language))
        language = this.$root.user.language
      axios.get(`${prefix}${book.title}:${language}`).then(
        response => {
          let chapters = [[]]
          response.data.results.forEach(chapter => {
            if (this.createChaptersColumn(chapters[chapters.length - 1]))
              chapters.push([])
            chapters[chapters.length - 1].push(chapter)
          });
          this.$root.books.push({
            'title': book.title,
            'language': language,
            'chapters': chapters,
            'order': book.order
          })
          this.$root.books.sort((a, b) => (a.order > b.order) ? 1 : -1)
        }
      )
    },
    syncBooks() {
      /*
      TODO: Fix book doubles problem
      TODO: Fix books sorting
      */
      if (this.loading || this.$root.books.length)
        return
      this.loading = !this.loading
      for (let [url, prefix] of [['quran', ''], ['hadith', 'hadith/']]) {
        axios.get(url).then(
          response => {
            for (let book of response.data.results) {
              this.addBook(book, prefix)
            }
          }
        )
      }
    },
  },
  data() {
    return {
      loading: false,
      texts: [],
      form: {
        book: {},
        chapter: {},
        text: {}
      }
    }
  },
  /* mounted() { */
  /*   this.syncBooks() */
  /* } */
}
</script>

<style>
.fs-0 {
    font-size: 130%
}
.arabic .fs-0 {
    font-size: 200%
}
.car-body {
    height: 125px;
    min-width: 90px;
    max-width: 90px;
    margin-right: 5px;
    padding-top: 70px;
    text-align: center;
    color: #666;
    font-size: 14px
}
.chapter-item {
    border-right: 5px solid #d2d2d2;
    margin: 0 16px 0 0;
    min-height: 21px;
    line-height: 20px;
    
}
.arabic .chapter-item {
    border-right: 0;
    margin: 0 0 0 16px!important;
    border-left: 5px solid #d2d2d2; margin-left: 0;
}
.chapter-item small {
    float: left; width: 15px; text-align: right
}
.chapter-item span {
    margin: 0 0 0 20px;
    display: block;
}
.arabic .chapter-item small {
    float: right; text-align: left
}
.arabic .chapter-item span {
    margin: 0 20px 0 0;
}
.text-ayat.text-item small {
    font-size: 11px;
    line-height: 25px;
    display: inline-block;
    border: 1px solid #d2d2d2;
    width: 25px;
    height: 25px;
    text-align: center;
    margin: 0 25px 0 13px;
    border-radius: 15px;
    position: relative;
    top: -2px;
}
.arabic .text-ayat.text-item small {
    margin: 0 13px 0 25px;
    top: -4px;
}
.text-ayat.text-item button {
    position: relative;
    font-size: 15px;
    margin: 0 21px -4px -54px;
    top: -3px;
}
.arabic .text-ayat.text-item button {
    margin: 0 -54px 0 21px;
    top: -5px;
}
.text-hadith button {
    position: absolute;
    margin-top: -48px;
    left: calc(50% - 16px);
}
.text-ayat {
    display: inline
}
.arabic .narrated {
    font-size: 16px;
    line-height: 24px;
}
</style>
