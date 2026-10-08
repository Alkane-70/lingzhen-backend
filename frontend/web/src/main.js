import { createApp } from 'vue'
import ElementPlus from 'element-plus'          // 👈 引入 Element Plus
import 'element-plus/dist/index.css'             // 👈 引入它的样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 👈 引入所有图标
import App from './App.vue'
import './assets/main.css'

const app = createApp(App)

// 👇 把所有图标注册为全局组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)  // 👈 注册 Element Plus
app.mount('#app')