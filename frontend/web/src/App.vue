<template>
  <div class="app-wrapper">
    <!-- 顶部 Header -->
    <header class="header">
      <div class="header-left">
        <div class="logo-icon">
          <el-icon :size="24" color="#fff"><FirstAidKit /></el-icon>
        </div>
        <div class="header-title">
          <h1>医疗知识库检索系统</h1>
          <p>基于循证医学资料的智能检索</p>
        </div>
      </div>
    </header>

    <!-- 主体内容区 -->
    <main class="main-content">
      <!-- 左侧聊天面板 -->
      <div class="panel chat-panel">
        <div class="panel-header">
          <h2>对话检索</h2>
          <!-- 模式切换 -->
          <div class="role-switch">
            <div 
              class="role-btn" 
              :class="{ active: currentRole === 'patient' }" 
              @click="currentRole = 'patient'"
            >
              <el-icon><User /></el-icon> 患者模式
            </div>
            <div 
              class="role-btn" 
              :class="{ active: currentRole === 'doctor' }" 
              @click="currentRole = 'doctor'"
            >
              <el-icon><UserFilled /></el-icon> 医生模式
            </div>
          </div>
          <p class="role-desc">
            当前：{{ currentRole === 'patient' ? '通俗易懂的健康科普' : '专业严谨的医学参考资料' }}
          </p>
        </div>

        <div class="panel-body">
          <!-- 空白时的提示区 -->
          <div v-if="chatHistory.length === 0" class="empty-state">
            <div class="empty-icon">
              <el-icon :size="30" color="#14b8a6"><Document /></el-icon>
            </div>
            <h3>输入您想查询的医学问题</h3>
            <p>系统将从知识库中检索相关资料</p>
            
            <div class="quick-examples">
              <div class="example-item" @click="queryInput = '高血压日常饮食要注意什么？'; handleSearch()">
                高血压日常饮食要注意什么？
              </div>
              <div class="example-item" @click="queryInput = '感冒发烧什么时候需要去医院？'; handleSearch()">
                感冒发烧什么时候需要去医院？
              </div>
            </div>
          </div>

          <!-- 历史对话区 -->
          <div v-else class="chat-history">
            <div v-for="(msg, index) in chatHistory" :key="index" :class="['message', msg.role]">
              <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
              <div class="text">{{ msg.content }}</div>
            </div>
          </div>
        </div>

        <!-- 底部输入框 -->
        <div class="chat-input-area">
          <textarea 
            v-model="queryInput" 
            rows="3"
            placeholder="请描述您的健康问题..."
            class="custom-textarea"
            @keyup.enter="handleSearch"
          ></textarea>
          <div class="input-footer">
            <span class="input-tip">Enter 发送, Shift + Enter 换行</span>
            <el-button type="primary" color="#14b8a6" :loading="isLoading" @click="handleSearch">
              <el-icon><Promotion /></el-icon> 发送
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧结果面板 -->
      <div class="right-panels">
        <!-- 知识图谱占位区 -->
        <div class="panel graph-panel">
          <div class="graph-placeholder">
            <el-icon :size="40" color="#14b8a6"><Share /></el-icon>
            <h3>知识图谱区域</h3>
            <p>预留位置，后续接入知识图谱可视化</p>
          </div>
        </div>

        <!-- 检索结果展示区 -->
        <div class="panel result-panel">
          <div v-if="!searchResult" class="empty-result">
            <el-icon :size="50" color="#9ca3af"><Search /></el-icon>
            <h3>暂无检索结果</h3>
            <p>在左侧输入问题后，结论与引用来源将显示在这里</p>
          </div>

          <div v-else class="result-card">
            <div class="card-header">
              <h3>{{ currentRole === 'doctor' ? '专业诊疗参考' : '健康科普结论' }}</h3>
              <el-tag :type="currentRole === 'doctor' ? 'danger' : 'success'" size="small">
                {{ currentRole === 'doctor' ? '医生版' : '患者版' }}
              </el-tag>
            </div>
            <el-divider />
            <div class="content">
              <p>{{ searchResult.summary }}</p>
            </div>
            
            <div class="citations">
              <h4>📚 知识来源（可溯源）：</h4>
              <ul>
                <li v-for="(cite, i) in searchResult.citations" :key="i">
                  <a href="#">{{ cite }}</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部合规声明 -->
    <footer class="footer">
      <el-icon><Warning /></el-icon>
      <span>本系统仅为健康科普/资料查阅辅助工具，不替代执业医师诊断</span>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
// 注意：这里移除了会报错的 Stethoscope，换成了 UserFilled
import { FirstAidKit, User, UserFilled, Document, Promotion, Share, Search, Warning } from '@element-plus/icons-vue'

const currentRole = ref('patient')
const queryInput = ref('')
const isLoading = ref(false)
const chatHistory = ref([])
const searchResult = ref(null)

const fetchMockData = (query, role) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (role === 'patient') {
        resolve({
          summary: `关于您提到的“${query}”，根据医学百科库综合检索，建议您保持良好的作息，症状持续请前往正规医院就诊。此结论仅做科普参考。`,
          citations: ['《内科学（第9版）》 人民卫生出版社', '中国居民健康指南 2023版']
        })
      } else {
        resolve({
          summary: `针对“${query}”的临床检索结果：最新临床指南推荐一线用药方案，需关注患者的个体化差异及药物相互作用。建议结合基因检测结果制定方案。`,
          citations: ['UpToDate 临床顾问', '《新英格兰医学杂志》 2024年最新综述', '脱敏临床案例库：病例编号 202406']
        })
      }
    }, 1500)
  })
}

const handleSearch = async () => {
  if (!queryInput.value.trim()) {
    ElMessage.warning('请输入检索内容')
    return
  }
  
  const userMessage = queryInput.value
  chatHistory.value.push({ role: 'user', content: userMessage })
  
  isLoading.value = true
  searchResult.value = null 
  
  const data = await fetchMockData(userMessage, currentRole.value)
  
  searchResult.value = data
  chatHistory.value.push({ role: 'ai', content: '已为您检索到相关资料，请查看右侧结论。' })
  
  isLoading.value = false
  queryInput.value = '' 
}
</script>

<style scoped>
.app-wrapper { display: flex; flex-direction: column; height: 100vh; width: 100vw; background-color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; box-sizing: border-box;}
.header { background-color: #fff; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center;}
.header-left { display: flex; align-items: center; gap: 12px;}
.logo-icon { background-color: #14b8a6; width: 40px; height: 40px; border-radius: 8px; display: flex; justify-content: center; align-items: center;}
.header-title h1 { font-size: 20px; margin: 0; color: #1f2937;}
.header-title p { font-size: 12px; margin: 2px 0 0 0; color: #6b7280;}

.main-content { display: flex; flex: 1; padding: 20px; gap: 20px; overflow: hidden;}
.panel { background-color: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f3f4f6; display: flex; flex-direction: column; overflow: hidden;}

.chat-panel { flex: 1; display: flex; flex-direction: column;}
.panel-header { padding: 20px; border-bottom: 1px solid #f3f4f6;}
.panel-header h2 { font-size: 16px; margin: 0 0 15px 0; color: #1f2937;}
.role-switch { display: flex; background-color: #f3f4f6; border-radius: 8px; padding: 4px; margin-bottom: 10px;}
.role-btn { flex: 1; text-align: center; padding: 8px 0; font-size: 14px; color: #6b7280; cursor: pointer; border-radius: 6px; display: flex; justify-content: center; align-items: center; gap: 6px; transition: all 0.2s;}
.role-btn.active { background-color: #fff; color: #0d9488; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-weight: 500;}
.role-desc { font-size: 12px; color: #6b7280; margin: 0;}

.panel-body { flex: 1; padding: 20px; overflow-y: auto; background-color: #fff; display: flex; flex-direction: column;}
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; color: #4b5563; gap: 8px;}
.empty-icon { background-color: #ccfbf1; width: 60px; height: 60px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-bottom: 10px;}
.quick-examples { display: flex; flex-direction: column; gap: 10px; width: 100%; margin-top: 20px;}
.example-item { padding: 12px 16px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; color: #4b5563; text-align: left; cursor: pointer; transition: all 0.2s;}
.example-item:hover { background-color: #f0fdfa; border-color: #14b8a6; color: #0f766e;}

.chat-history { display: flex; flex-direction: column; gap: 15px;}
.message { display: flex; gap: 10px; max-width: 80%;}
.message.user { align-self: flex-end; flex-direction: row-reverse;}
.avatar { width: 32px; height: 32px; border-radius: 50%; background-color: #14b8a6; color: #fff; display: flex; justify-content: center; align-items: center; font-size: 14px; font-weight: bold; flex-shrink: 0;}
.message.user .avatar { background-color: #3b82f6;}
.message .text { padding: 10px 15px; border-radius: 8px; font-size: 14px; line-height: 1.5; color: #1f2937; background-color: #f3f4f6;}
.message.user .text { background-color: #ccfbf1; color: #0f766e;}

.chat-input-area { padding: 20px; border-top: 1px solid #f3f4f6; background-color: #fff;}
:deep(.el-textarea__inner) { border-radius: 8px; border: 1px solid #e5e7eb; padding: 10px; font-size: 14px; resize: none; box-shadow: none;}
:deep(.el-textarea__inner:focus) { border-color: #14b8a6; box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.1);}
.custom-textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}
.custom-textarea:focus {
  border-color: #14b8a6;
  box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.1);
}
.input-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px;}
.input-tip { font-size: 12px; color: #9ca3af;}

.right-panels { flex: 1; display: flex; flex-direction: column; gap: 20px; overflow: hidden;}
.graph-panel { flex: 1; min-height: 200px;}
.graph-placeholder { width: 100%; height: 100%; border: 2px dashed #d1d5db; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #6b7280; gap: 10px; margin: 15px; width: calc(100% - 30px); height: calc(100% - 30px);}
.graph-placeholder h3 { margin: 0; font-size: 16px; color: #4b5563;}
.graph-placeholder p { margin: 0; font-size: 12px; color: #9ca3af;}

.result-panel { flex: 1.5; overflow-y: auto;}
.empty-result { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #9ca3af; gap: 10px;}
.empty-result h3 { margin: 0; font-size: 16px; color: #4b5563;}
.empty-result p { margin: 0; font-size: 12px; color: #9ca3af;}

.result-card { padding: 20px; height: 100%;}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
.card-header h3 { margin: 0; font-size: 16px; color: #1f2937;}
.content { margin-bottom: 20px; font-size: 14px; color: #4b5563; line-height: 1.6;}
.citations h4 { font-size: 14px; color: #1f2937; margin: 0 0 10px 0;}
.citations ul { padding-left: 20px; margin: 0; font-size: 13px; color: #6b7280;}
.citations a { color: #14b8a6; text-decoration: none;}
.citations a:hover { text-decoration: underline;}

.footer { background-color: #fef3c7; color: #92400e; padding: 12px; display: flex; justify-content: center; align-items: center; gap: 8px; font-size: 14px; border-top: 1px solid #fde68a;}

@media (max-width: 768px) {
  .main-content { flex-direction: column; }
  .chat-panel, .right-panels { flex: none; height: 500px; }
}
</style>