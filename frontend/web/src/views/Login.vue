<template>
  <div class="login-page">
    <!-- 背景视频 -->
    <video class="bg-video" autoplay loop muted playsinline>
      <source src="/images/index_bg.mp4" type="video/mp4">
    </video>

    <!-- 登录框 -->
    <div class="login-container">
      <div class="first_box">
        <div class="content">
          <h1>{{ activeTab === 'login' ? 'Sign In to Your Account' : 'Create New Account' }}</h1>
          <p>{{ activeTab === 'login' ? 'Enter Your Account & Password' : 'Fill in to register' }}</p>

          <!-- 双人头像（三态切换） -->
          <div class="avatar-group">
            <!-- 默认状态 -->
            <div class="avatar-state" :class="{ active: avatarState === 0 }">
              <img src="/images/doctor-close.png" alt="医生默认">
              <img src="/images/nurse-close.png" alt="护士默认">
            </div>
            <!-- 输入账号状态 -->
            <div class="avatar-state" :class="{ active: avatarState === 1 }">
              <img src="/images/doctor-open.png" alt="医生输账号">
              <img src="/images/nurse-open.png" alt="护士输账号">
            </div>
            <!-- 输入密码状态 -->
            <div class="avatar-state" :class="{ active: avatarState === 2 }">
              <img src="/images/doctor-close.png" alt="医生输密码">
              <img src="/images/nurse-close.png" alt="护士输密码">
            </div>
          </div>
        </div>
      </div>

      <div class="second_box">
        <!-- 自定义 Tab 切换 -->
        <div class="tab-switch">
          <div class="tab-item" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">登录</div>
          <div class="tab-item" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">注册</div>
        </div>

        <!-- 账号输入 -->
        <div class="logo-input form-item">
          <img src="/images/account(1).jpg" alt="账号">
          <input
            type="text"
            :placeholder="activeTab === 'login' ? '请输入账号' : '设置用户名'"
            v-model="form.username"
            @focus="avatarState = 1"
            @blur="avatarState = 0"
          >
        </div>

        <!-- 密码输入 -->
        <div class="logo-input form-item">
          <img src="/images/password(1).jpg" alt="密码">
          <input
            type="password"
            :placeholder="activeTab === 'login' ? '请输入密码' : '设置密码'"
            v-model="form.password"
            @focus="avatarState = 2"
            @blur="avatarState = 0"
          >
        </div>

        <!-- 登录/注册按钮 -->
        <div class="form-item">
          <button type="button" @click="activeTab === 'login' ? handleLogin() : handleRegister()">
            {{ activeTab === 'login' ? 'Sign In' : 'Sign Up' }}
          </button>
        </div>

        <!-- 底部切换提示 -->
        <div class="form-item switch-tip">
          <span v-if="activeTab === 'login'">
            Don't have an account?
            <a @click="activeTab = 'register'">Sign Up</a>
          </span>
          <span v-else>
            Already have an account?
            <a @click="activeTab = 'login'">Sign In</a>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const activeTab = ref('login')
const avatarState = ref(0) // 0=默认 1=输账号 2=输密码
const form = ref({ username: '', password: '' })

// 登录（接口完全保留）
const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/login', {
      username: form.value.username,
      password: form.value.password
    })
    if (res.data.code === 200) {
      localStorage.setItem('user_id', res.data.user_id)
      localStorage.setItem('username', res.data.username)
      ElMessage.success('登录成功！')
      emit('login-success')
    } else {
      ElMessage.error(res.data.msg || '登录失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('登录失败，请检查后端服务')
  }
}

// 注册（接口完全保留）
const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/register', {
      username: form.value.username,
      password: form.value.password
    })
    if (res.data.code === 200) {
      ElMessage.success('注册成功，请登录！')
      activeTab.value = 'login'
      form.value.password = ''
    } else {
      ElMessage.error(res.data.msg || '注册失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('注册失败，请检查后端服务')
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  min-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  border-radius: 8px;
}
.bg-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}
.login-container {
  width: 480px;
  z-index: 1;
}
.first_box {
  background: transparent;                 /* 👈 完全透明 */
  /* 删掉 backdrop-filter */
  border-radius: 20px 20px 0 0;
  padding: 16px 20px 0 20px;
  box-shadow: none;                        /* 👈 去掉阴影，避免在透明背景上出现阴影框 */
}
.content {
  text-align: center;
}

.content h1, .content p {
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.8);
}

.content h1 {
  color: rgb(52, 109, 174);      /* 更深的蓝色 */
  font-size: 24px;
  font-weight: 700;    /* 👈 加粗 */
  margin: 0 0 8px 0;
}
.content p {
  color: #2b6eba;
  font-size: 14px;
  margin: 0 0 20px 0;
}
.avatar-group {
  position: relative;
  width: 100%;
  height: 140px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  overflow: hidden;
  margin-bottom: -4px;
}
.avatar-state {
  position: absolute;
  width: 100%;
  height: 100%;
  display: none;
  justify-content: center;
  gap: 120px;
  align-items: center;
}
.avatar-state.active {
  display: flex;
}
.avatar-state img {
  width: 130px;
  height: 130px;
  object-fit: contain;
  object-position: center bottom;
  margin-bottom: -10px;
  transition: transform 0.3s ease;
}
.second_box {
  background: #fff;
  border-radius: 0 0 20px 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}
.tab-switch {
  display: flex;
  background: #f3f4f6;
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 20px;
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 15px;
  color: #6b7280;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}
.tab-item.active {
  background: #14b8a6;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(20, 184, 166, 0.3);
}
.form-item {
  margin-bottom: 14px;
}
.logo-input {
  position: relative;
}
.logo-input input {
  width: 100%;
  padding: 14px 12px 14px 45px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.logo-input input:focus {
  border-color: #14b8a6;
  box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.1);
}
.logo-input img {
  position: absolute;
  width: 24px;
  height: 24px;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  object-fit: contain;
}
.form-item button {
  width: 100%;
  padding: 14px 0;
  background: #14b8a6;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.form-item button:hover {
  background: #0d9488;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
}
.switch-tip {
  text-align: center;
  font-size: 13px;
  color: #6b7280;
  margin-top: 10px;
}
.switch-tip a {
  color: #14b8a6;
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
}
.switch-tip a:hover {
  text-decoration: underline;
}
</style>