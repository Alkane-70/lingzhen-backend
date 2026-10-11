<template>
  <div class="history-wrapper">
    <div class="history-header">
      <h2>📋 我的健康档案</h2>
      <p>当前用户：{{ username }}</p>
    </div>

    <div v-if="records.length === 0" class="empty-state">
      <el-icon :size="60" color="#9ca3af"><Document /></el-icon>
      <h3>您还没有问诊记录</h3>
      <p>快去体验智能问诊吧！</p>
    </div>

    <div v-else class="records-list">
      <el-collapse v-model="activeNames">
        <el-collapse-item
          v-for="(record, index) in records"
          :key="index"
          :name="index"
        >
          <template #title>
            <div class="collapse-title">
              <span class="symptom">🩺 {{ record.symptom }}</span>
              <span class="record-time">📅 问诊时间：{{ formatTime(record.created_at) }}</span>
              <el-tag
                :type="record.severity === 'severe' ? 'danger' : 'success'"
                size="small"
                style="margin-left: 10px;"
              >
                {{ record.severity === 'severe' ? '⚠️ 重症' : '✅ 轻症' }}
              </el-tag>
            </div>
          </template>

          <div class="record-body">
            <p><strong>建议科室：</strong>{{ record.department || '全科门诊' }}</p>
            <p><strong>理由：</strong>{{ record.reason || '暂无明确理由' }}</p>
            <p class="confidence">置信度：{{ record.confidence ? (record.confidence * 100).toFixed(1) : 0 }}%</p>

            <div v-if="record.chat_history && record.chat_history.length > 0" class="detail-panel">
              <div class="detail-title">💬 问诊对话记录</div>
              <div
                v-for="(msg, i) in record.chat_history"
                :key="i"
                :class="['chat-bubble', msg.role === 'user' ? 'chat-user' : 'chat-ai']"
              >
                <span class="bubble-avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</span>
                <span class="bubble-text">{{ msg.content }}</span>
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'

const records = ref([])
const username = ref(localStorage.getItem('username') || '未登录')
const activeNames = ref([])

const formatTime = (timeStr) => {
  if (!timeStr) return '近期'
  return String(timeStr).slice(0, 16).replace('T', ' ')
}

onMounted(async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/history/${userId}`)
    records.value = res.data.filter(record =>
      record.reason && record.reason.trim() !== '' &&
      record.department && record.department !== '综合科' &&
      record.confidence && record.confidence >= 0.6
    )
    console.log('📚 历史记录:', records.value)
  } catch (e) {
    console.error(e)
    ElMessage.error('获取历史记录失败，请检查后端服务')
  }
})
</script>

<style scoped>
.history-wrapper {
  padding: 30px;
  height: 100vh;
  overflow-y: auto;
  background-color: #f8fafc;
}
.history-header {
  margin-bottom: 24px;
}
.history-header h2 {
  margin: 0;
  color: #1f2937;
}
.history-header p {
  margin: 6px 0 0 0;
  color: #6b7280;
  font-size: 14px;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #9ca3af;
  gap: 12px;
}
.records-list {
  max-width: 900px;
  margin: 0 auto;
}
.collapse-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.symptom {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}
.record-time {
  font-size: 12px;
  color: #9ca3af;
}
.record-body p {
  margin: 6px 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
}
.confidence {
  color: #9ca3af !important;
  font-size: 12px !important;
}
.detail-panel {
  margin-top: 12px;
  padding: 12px;
  background-color: #f0fdfa;
  border-radius: 8px;
  border-left: 3px solid #14b8a6;
}
.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #0d9488;
  margin-bottom: 8px;
}
.chat-bubble {
  display: flex;
  gap: 8px;
  margin: 8px 0;
  align-items: flex-start;
}
.chat-user {
  flex-direction: row-reverse;
}
.bubble-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #14b8a6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
.chat-user .bubble-avatar {
  background: #3b82f6;
}
.bubble-text {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  background: #fff;
  color: #1f2937;
  max-width: 80%;
  line-height: 1.5;
}
.chat-user .bubble-text {
  background: #ccfbf1;
  color: #0f766e;
}
</style>