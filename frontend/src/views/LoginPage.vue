<template>
    <el-page-header :icon="ArrowLeft" title="返回" @back="goBack">
        
    </el-page-header>
    <el-row class="login-page">
        <el-col :span="6" :offset="9" class="form">
            <!-- 注册表单 -->
            <el-form v-if="isRegister" ref="form" size="large" autocomplete="off" :model="formModel" :rules="rules">
                <el-form-item>
                    <h1>注册</h1>
                </el-form-item>
                <el-form-item prop="username">
                    <el-input :prefix-icon="User" placeholder="请输入用户名" v-model="formModel.username"></el-input>
                </el-form-item>
                <el-form-item prop="email">
                    <el-input :prefix-icon="Message" placeholder="请输入邮箱" v-model="formModel.email"></el-input>
                </el-form-item>
                <el-form-item prop="phone">
                    <el-input :prefix-icon="Iphone" placeholder="请输入手机号" v-model="formModel.phone"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                      :prefix-icon="Lock"
                      type="password"
                      placeholder="请输入密码"
                      v-model="formModel.password"
                      @keyup.enter="register"
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="register" class="button">
                        注册
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-link type="info" :underline="false" @click="isRegister = false">
                        ← 返回
                    </el-link>
                </el-form-item>
            </el-form>
            <!-- 登录表单 -->
            <el-form v-else ref="form" size="large" autocomplete="off" :model="formModel" :rules="rules">
                <el-form-item>
                    <h1>登录</h1>
                </el-form-item>
                <el-form-item prop="username">
                    <el-input :prefixIcon="User" placeholder="请输入用户名" v-model="formModel.username"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                      name="password"
                      :prefixIcon="Lock"
                      type="password"
                      placeholder="请输入密码"
                      v-model="formModel.password"
                      @keyup.enter="login"
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <div class="flex">
                        <el-checkbox>记住我</el-checkbox>
                        <el-link type="primary" :underline="false">忘记密码?</el-link>
                    </div>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" auto-insert-space @click="login" class="button">
                        登录
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-link type="info" :underline="false" @click="isRegister = true">
                        注册
                    </el-link>
                </el-form-item>
            </el-form>
        </el-col>
    </el-row>
</template>

<script setup>
import { ref, watch } from 'vue';
// import { ElMessage } from 'element-plus';
import { User, Lock, Message, Iphone, ArrowLeft } from '@element-plus/icons-vue'
import { registerUser, loginUser } from '@/api/user'
import { useRouter } from 'vue-router';

import { useUserStore } from '@/stores';
import { storeToRefs } from 'pinia';

const userStore = useUserStore()

const {
        setToken,
        removeToken
      } = userStore

const {
        token
      } = storeToRefs(userStore)

const isRegister = ref(true)
const form = ref('')
const router = useRouter()
const formModel = ref({
    username: '',
    email: '',
    phone: '',
    password: ''
})

const rules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' }
    ],
    phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
    ]
}

const register = async () => {
    await form.value.validate()
    await registerUser(formModel.value)
    ElMessage.success('注册成功')
    // 切换到登录
    isRegister.value = false
}

const login = async () => {
    await form.value.validate()
    const res = await loginUser(formModel.value)
    console.log(res)
    setToken(res.access_token)
    ElMessage.success('登录成功')
    router.push('/index')
}

const goBack= () => {
    router.go(-1)
}

watch(isRegister, () => {
    formModel.value = {
        username: '',
        email: '',
        phone: '',
        password: ''
    }
})
</script>

<style scoped>
.login-page {
    height: 100vh;
    background-color: #fff;
}
.form {
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.flex {
    width: 100%;
    display: flex;
    justify-content: space-between;
}
.button {
    width: 100%;
}
</style>