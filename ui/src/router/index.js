import { createRouter, createWebHistory } from 'vue-router'
import TopicListView from '../views/TopicListView.vue'
import TopicOneView from '../views/TopicOneView.vue'

const routes = [
  {
    path: '/',
    name: 'topic_list',
    component: TopicListView
  },
  {
    path: '/topic/:topic_id',
    name: 'topic_one',
    component: TopicOneView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
