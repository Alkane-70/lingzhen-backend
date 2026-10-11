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
      <div v-for="(record, index) in records" :key="index" class="record-card">
        <div class="record-header">
          <div class="record-title">
            <span class="symptom">🩺 {{ record.symptom }}</span>
          </div>
          <el-tag
            :type="record.severity === 'severe' ? 'danger' : 'success'"
            size="small"
          >
            {{ record.severity === 'severe' ? '⚠️ 重症' : '✅ 轻症' }}
          </el-tag>
        </div>
        <div class="record-body">
          <p><strong>建议科室：</strong>{{ record.department }}</p>
          <p><strong>理由：</strong>{{ record.reason }}</p>
          <p class="confidence">置信度：{{ record.confidence ? (record.confidence * 100).toFixed(1) : 0 }}%</p>
        </div>
      </div>
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

onMounted(async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/history/${userId}`)
    records.value = res.data
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
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
}
.record-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #14b8a6;
}
.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.symptom {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
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
</style>