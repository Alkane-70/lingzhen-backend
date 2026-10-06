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
            <!-- 1. 这里是循环显示历史消息（保留你原来的） -->
            <div v-for="(msg, index) in chatHistory" :key="index" :class="['message', msg.role]">
              <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
              <div class="text">{{ msg.content }}</div>
            </div>

            <!-- 2. 👇 这是新增的：AI 推理中 Loading 动画（只在加载时显示） -->
            <div v-if="isLoading" class="message ai">
              <div class="avatar">AI</div>
              <div class="text loading-bubble">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
                <span style="margin-left: 8px;">AI 正在推理中...</span>
              </div>
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
        <!-- 知识图谱区（ECharts） -->
        <div class="panel graph-panel">
          <!-- 加载状态 -->
          <div v-if="isGraphLoading" class="graph-loading">
            <el-icon class="is-loading" :size="40" color="#14b8a6"><Loading /></el-icon>
            <h3>正在构建知识图谱...</h3>
          </div>
          
          <!-- 👇 新增：图谱缩放按钮 -->
          <div class="graph-controls">
            <button @click="zoomGraph(1.2)">➕ 放大</button>
            <button @click="zoomGraph(0.8)">➖ 缩小</button>
            <button @click="zoomGraph(1, true)">🔄 复位</button>
          </div>

          <!-- ECharts 容器 -->
          <div v-show="!isGraphLoading && searchResult" ref="chartRef" class="chart-container"></div>
          
          <!-- 无数据时的占位 -->
          <div v-if="!isGraphLoading && !searchResult" class="graph-placeholder">
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

            <!-- 👇 新增：一键复制分诊结果 -->
            <div class="action-buttons">
              <el-button type="success" plain @click="copyResult">
                <el-icon><CopyDocument /></el-icon> 一键复制分诊结果
              </el-button>
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
import { ref, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import * as echarts from 'echarts'
import { FirstAidKit, User, UserFilled, Document, Promotion, Share, Search, Warning, Loading, CopyDocument } from '@element-plus/icons-vue'

const currentRole = ref('patient')
const queryInput = ref('')
const isLoading = ref(false)
const isGraphLoading = ref(false)
const chatHistory = ref([])
const searchResult = ref(null)

// ECharts 相关
const chartRef = ref(null)
let myChart = null

// 模拟后端返回（头晕恶心专门定制，其他走通用图谱）
const fetchMockData = (query, role) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 1. 先定义“通用兜底图谱”（其他所有词都走这个）
      let graphData = {
        nodes: [
          { name: query, category: 1, symbolSize: 65 }, // 把用户输入当作核心疾病/关键词
          { name: '常见症状A', category: 0, symbolSize: 45 },
          { name: '常见症状B', category: 0, symbolSize: 45 },
          { name: '相关科室', category: 2, symbolSize: 55 },
          { name: '建议检查', category: 3, symbolSize: 45 }
        ],
        links: [
          { source: query, target: '常见症状A', value: '可能症状' },
          { source: query, target: '常见症状B', value: '伴随症状' },
          { source: query, target: '相关科室', value: '就诊科室' },
          { source: query, target: '建议检查', value: '建议检查' }
        ]
      }

      // 2. 如果输入包含“头晕”或“恶心”，就用专门定制的完整图谱覆盖掉通用版
      if (query.includes('头晕') || query.includes('恶心')) {
        graphData = {
          nodes: [
            { name: '头晕', category: 0, symbolSize: 55 }, // 症状（黄）
            { name: '恶心', category: 0, symbolSize: 45 }, // 症状（黄）
            { name: '高血压', category: 1, symbolSize: 60 }, // 疾病（红）
            { name: '脑卒中', category: 1, symbolSize: 55 }, // 疾病（红）
            { name: '神经内科', category: 2, symbolSize: 55 }, // 科室（蓝）
            { name: '心血管内科', category: 2, symbolSize: 55 } // 科室（蓝）
          ],
          links: [
            { source: '头晕', target: '高血压', value: '常见症状' },
            { source: '恶心', target: '高血压', value: '伴随症状' },
            { source: '头晕', target: '脑卒中', value: '预警症状' },
            { source: '高血压', target: '心血管内科', value: '就诊' },
            { source: '脑卒中', target: '神经内科', value: '就诊' },
            { source: '头晕', target: '神经内科', value: '直接就诊' }
          ]
        }
      }

      // 根据角色生成不同摘要
      const summary = role === 'patient' 
        ? `关于您提到的“${query}”，根据医学百科库综合检索，建议您注意休息。若症状持续，请前往正规医院就诊。此结论仅做科普参考。`
        : `针对“${query}”的临床检索结果：需结合具体症状排查病因，建议进行相关检查。此结论仅供参考。`

      resolve({
        summary,
        citations: ['《内科学（第9版）》 人民卫生出版社', '中国居民健康指南 2023版'],
        graphData
      })
    }, 1500)
  })
}

// 核心检索
const handleSearch = async () => {
  if (!queryInput.value.trim()) {
    ElMessage.warning('请输入检索内容')
    return
  }
  
  const userMessage = queryInput.value
  chatHistory.value.push({ role: 'user', content: userMessage })
  
  isLoading.value = true
  isGraphLoading.value = true // 开启图谱 loading
  searchResult.value = null 
  
  // 👇 新增：彻底销毁旧的 ECharts 实例，连骨头都不剩
  if (myChart) {
    myChart.dispose()
    myChart = null // 置空，强制下一次重新 init
  }
  
  const data = await fetchMockData(userMessage, currentRole.value)
  
  // 新增：置信度判断逻辑（放在 data 获取之后,改成轻量级顶部提示，不遮挡画面,改成右上角悬浮通知，永不自动消失）
  const confidence = Math.random() * 100 
  if (confidence < 80) {
    ElNotification({
      title: '⚠️ 急诊建议',
      message: `本次检索结果的置信度较低（${confidence.toFixed(1)}%），系统无法给出准确参考。建议您立即前往正规医院的急诊科就诊，以免延误病情！`,
      type: 'warning',
      duration: 0, // 👈 关键：设置为 0 表示不自动关闭
      position: 'top-right', // 悬浮在右上角
      showClose: true, // 显示关闭按钮
      customClass: 'custom-notification' // 自定义样式
    })
  }

  searchResult.value = data
  isLoading.value = false
  
  // 等待 DOM 更新后，渲染图谱
  nextTick(() => {
    setTimeout(() => {
      isGraphLoading.value = false
      renderGraph(data.graphData)
    }, 800) // 模拟科技感的渲染延迟
  })
  
  chatHistory.value.push({ role: 'ai', content: '已为您检索到相关资料，请查看右侧结论。' })
  queryInput.value = '' 
}

// 渲染 ECharts 图谱
// 渲染 ECharts 图谱（最终修复版）
const renderGraph = (graphData) => {
  if (!chartRef.value) return
  
  // 1. 销毁旧的实例，确保重新初始化能拿到正确的尺寸
  if (myChart) {
    myChart.dispose()
  }
  myChart = echarts.init(chartRef.value)

  const categories = [
    { name: '症状', itemStyle: { color: '#f59e0b' } },
    { name: '疾病/建议', itemStyle: { color: '#ef4444' } },
    { name: '科室', itemStyle: { color: '#3b82f6' } }
  ]

  const option = {
    tooltip: {},
    legend: { 
      data: categories.map(c => c.name), 
      bottom: 10,
      left: 'center'
    },
    series: [{
      type: 'graph',
      layout: 'force', 
      data: graphData.nodes,
      links: graphData.links,
      categories: categories,
      roam: true, 
      center: ['50%', '50%'], 
      zoom: 1.2,
      label: { 
        show: true, 
        position: 'right', 
        formatter: '{b}',
        fontSize: 14,
        color: '#1f2937'
      },
      force: {
        repulsion: 1500, // 斥力调小一点，让节点不至于飞出屏幕
        edgeLength: 150, // 连线长度
        gravity: 0.1,    // 加大重力，把节点往中间拉
        layoutAnimation: true 
      },
      // 新增：显示连线上的关系文字（比如“常见症状”、“就诊”）
      edgeLabel: {
        show: true,
        formatter: '{c}', // 显示数据里 value 的值
        fontSize: 12,
        color: '#6b7280'
      },
      lineStyle: { 
        color: 'source', 
        curveness: 0.1,
        width: 2,
        // 新增：动态粒子流动效果，让连线看起来有数据在流动
        type: 'solid', 
        curveness: 0.2,
        opacity: 0.8,
      },
      // 👇 新增：节点高亮时的脉冲光晕效果
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.3)'
      },
      // 👇 新增：连线上的箭头，增强推理方向感（从症状指向疾病）
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
      emphasis: { 
        focus: 'adjacency', 
        lineStyle: { width: 4 } 
      }
    }]
  }

  myChart.setOption(option, true)
  
  // 👇 关键修复：强制 resize，解决缩在左上角的问题
  myChart.resize()
  setTimeout(() => {
    if (myChart) myChart.resize()
  }, 200)

  // 监听窗口变化，自适应
  window.addEventListener('resize', () => { myChart && myChart.resize() })
}

// 图谱缩放控制
const zoomGraph = (factor, isReset = false) => {
  if (!myChart) return
  
  // 获取当前图表的配置
  const option = myChart.getOption()
  let currentZoom = option.series[0].zoom || 1
  
  if (isReset) {
    currentZoom = 1 // 复位
  } else {
    currentZoom = currentZoom * factor // 按比例放大或缩小
  }
  
  // 限制缩放范围，防止图飞走或者缩成一个点
  currentZoom = Math.max(0.3, Math.min(currentZoom, 4))
  
  // 更新图表
  myChart.setOption({
    series: [{
      zoom: currentZoom
    }]
  })
}

// 👇 新增：一键复制分诊结果
const copyResult = () => {
  if (!searchResult.value) return
  
  // 把结论和来源拼成一段文本
  const text = `【${currentRole.value === 'doctor' ? '医生版' : '患者版'}检索结果】\n` +
               `结论：${searchResult.value.summary}\n` +
               `引用来源：\n${searchResult.value.citations.join('\n')}`
  
  // 调用浏览器剪贴板 API 复制
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('分诊结果已复制到剪贴板！')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}



// 清理
onBeforeUnmount(() => {
  if (myChart) myChart.dispose()
})
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

.right-panels { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  /* 👇 把 overflow: hidden 改成下面这两个，防止内容被挤压 */
  overflow-y: auto; 
  min-height: 0; 
}
.graph-panel { 
  /* 👇 不要用 flex:1，改用固定高度，保证图谱绝对有位置显示 */
  flex: none;
  height: 350px; 
  position: relative; 
  display: flex; 
  flex-direction: column; 
  background-color: #fff;
}
.graph-loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #14b8a6; background-color: rgba(255,255,255,0.9); z-index: 10; gap: 15px; }
.chart-container {
  width: 100%;
  height: 100%;
  /* 👇 删掉 min-height，因为父级已经限制了高度，它只需要100%填满即可 */
  /* 删掉 display: flex, justify-content, align-items */
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background-color: #fafafa;
  position: absolute; 
  top: 0;
  left: 0;
}

/* 图谱缩放按钮样式 */
.graph-controls {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 20;
  display: flex;
  gap: 8px;
}
.graph-controls button {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s;
}
.graph-controls button:hover {
  background: #f0fdfa;
  border-color: #14b8a6;
  color: #0f766e;
}

.graph-placeholder { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #6b7280; gap: 10px; }
.graph-placeholder h3 { margin: 0; font-size: 16px; color: #4b5563;}
.graph-placeholder p { margin: 0; font-size: 12px; color: #9ca3af;}

.result-panel { 
  /* 👇 让它自动撑开剩下的高度 */
  flex: 1; 
  overflow-y: auto;
}
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

/* 一键复制按钮：改成精致的一行小胶囊 */
.action-buttons {
  margin-top: 15px;
  text-align: center;       /* 居中，如果靠右改 right */
  border-top: 1px dashed #e5e7eb;
  padding-top: 15px;
  display: flex;            /* 用 flex 控制对齐 */
  justify-content: center;  /* 居中，想靠右改 flex-end */
}

/* 👇 强制覆盖 Element Plus 的默认尺寸 */
.action-buttons .el-button {
  height: 28px !important;        /* 定死高度，不让它撑大 */
  padding: 0 12px !important;     /* 左右留一点空隙即可 */
  font-size: 12px !important;     /* 字号缩小 */
  border-radius: 14px !important; /* 胶囊形 */
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* 👇 图标也要跟着变小，并且和文字保持一行 */
.action-buttons .el-button .el-icon {
  font-size: 14px !important;
  margin-right: 4px !important;    /* 图标和文字之间的小间距 */
  vertical-align: middle !important;
}
.footer { background-color: #fef3c7; color: #92400e; padding: 12px; display: flex; justify-content: center; align-items: center; gap: 8px; font-size: 14px; border-top: 1px solid #fde68a;}

@media (max-width: 768px) {
  .main-content { flex-direction: column; }
  .chat-panel, .right-panels { flex: none; height: 500px; }
}

/* 自定义置信度警告提示 */
.custom-warning-msg {
  min-width: 300px !important;
  max-width: 500px !important;
  font-size: 13px !important;
  line-height: 1.5 !important;
  padding: 10px 16px !important;
  border-radius: 8px !important;
}
/* 自定义通知样式 */
.custom-notification {
  width: 320px !important;
  font-size: 13px !important;
  line-height: 1.5 !important;
}

/* 👇 强制把 Element Plus 那个巨大的感叹号压回去 */
.custom-notification .el-notification__icon {
  font-size: 24px !important;
  width: 24px !important;
  height: 24px !important;
}

.custom-notification .el-notification__content {
  font-size: 13px !important;
  line-height: 1.5 !important;
}

.custom-notification .el-notification__title {
  font-size: 14px !important;
  font-weight: 600 !important;
}

/* 👇 AI 推理中的 Loading 气泡样式 */
.loading-bubble {
  display: flex;
  align-items: center;
  background-color: #f0fdfa !important; /* 浅青色背景 */
  color: #0f766e !important;
  padding: 10px 16px !important;
  font-style: italic;
}

/* 三个跳动的小点 */
.loading-bubble .dot {
  width: 6px;
  height: 6px;
  background-color: #14b8a6;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-bubble .dot:nth-child(1) { animation-delay: -0.32s; }
.loading-bubble .dot:nth-child(2) { animation-delay: -0.16s; }

/* 跳动动画 */
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>