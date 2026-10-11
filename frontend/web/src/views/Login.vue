<template>
  <div class="login-wrapper">
    <div class="login-box">
      <div class="logo-area">
        <el-icon :size="40" color="#14b8a6"><FirstAidKit /></el-icon>
        <h1>灵诊智库</h1>
        <p>基于循证医学资料的智能检索</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-width="0">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" show-password />
            </el-form-item>
            <el-button type="primary" color="#14b8a6" size="large" style="width: 100%" @click="handleLogin">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" label-width="0">
            <el-form-item>
              <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" size="large" show-password />
            </el-form-item>
            <el-button type="success" size="large" style="width: 100%" @click="handleRegister">
              注册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { FirstAidKit } from '@element-plus/icons-vue'

const emit = defineEmits(['login-success'])

const activeTab = ref('login')
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '' })

// 登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
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

// 注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/register', {
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    if (res.data.code === 200) {
      ElMessage.success('注册成功，请登录！')
      activeTab.value = 'login'
      loginForm.value.username = registerForm.value.username
      loginForm.value.password = ''
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
.login-wrapper {
  width: 100%;
  padding: 10px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
}
.login-box {
  width: 420px;
  background: #fff;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}
.logo-area {
  text-align: center;
  margin-bottom: 30px;
}
.logo-area h1 {
  margin: 12px 0 4px 0;
  font-size: 24px;
  color: #1f2937;
}
.logo-area p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}
.login-tabs :deep(.el-tabs__item) {
  font-size: 15px;
}
</style>