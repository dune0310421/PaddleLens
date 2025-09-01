import { createRouter, createWebHistory } from 'vue-router'

// 页面组件
import Home from '../components/Home.vue'
import DeveloperSkills from '../views/DeveloperSkills.vue'
import Collaboration from '../views/Collaboration.vue'
import Community from '../views/Community.vue'

// 配置所有路由
const routes = [
  { path: '/', component: Home },
  { path: '/developerskills', component: DeveloperSkills },
  { path: '/collaboration', component: Collaboration },
  { path: '/community', component: Community }
]

// 创建路由对象并导出
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router