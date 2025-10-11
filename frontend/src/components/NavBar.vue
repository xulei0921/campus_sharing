<template>
    <el-header class="navbar">
        <div class="container">
            <div class="logo" @click="$router.push('/index')">校园共享</div>

            <el-menu
              :default-active="activePath"
              mode="horizontal"
              @select="handleSelect"
              class="menu"
            >
                <el-menu-item index="/index">首页</el-menu-item>
                <el-menu-item index="/items/create">发布物品</el-menu-item>
                <el-menu-item index="/my-items">我的物品</el-menu-item>
                <el-menu-item index="/transactions">我的交易</el-menu-item>
                <el-menu-item index="/chats">消息</el-menu-item>
            </el-menu>

            <div class="user-actions">
                
                <el-dropdown v-if="isLogin()">
                    <div class="el-dropdown-link">
                        <el-avatar @click="$router.push('/profile')" class="avatar">
                            <img src="https://picsum.photos/200/200" alt="用户头像">
                        </el-avatar>
                        <span class="username">{{ currentUser.username || '未登录'}}</span>
                        <el-icon class="el-dropdown-icon">
                            <arrow-down />
                        </el-icon>
                    </div>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
                            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
                <div v-else class="not-login" @click="$router.push('/login')">
                    <el-avatar :icon="UserFilled"></el-avatar>
                    <span>去登录</span>
                </div>
            </div>
        </div>
    </el-header>
    <!-- <button @click="fetchCurrentUser">测试</button> -->
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores'
import { getCurrentUser } from '@/api/user'

const route = useRoute()
const router = useRouter()
const currentUser = ref({})

const userStore = useUserStore()

const {
        removeToken,
        isLogin
      } = userStore

const activePath = computed(() => {
    return route.path
})

const handleSelect = (index) => {
    window.location.href = index
}

const logout = () => {
    removeToken()
    router.push('/')
    ElMessage.success("退出登录成功")
    window.location.reload()
}

const fetchCurrentUser = async () => {
    const data = await getCurrentUser() || {}
    currentUser.value = data
    console.log(currentUser.value)
}

onMounted(() => {
    if (isLogin()) {
        fetchCurrentUser()
    }
})
</script>

<style scoped>
.navbar {
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 0;
}
.container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}
.logo {
    font-size: 20px;
    font-weight: bold;
    color: #409eff;
    cursor: pointer;
}
.menu {
    flex: 1;
    margin: 0 20px;
}
.avatar {
    cursor: pointer;
}

.el-dropdown-link {
    cursor: pointer;
    display: flex;
    align-items: center;
}

.el-dropdown-icon {
    transition: transform 0.3s ease;
}

.el-dropdown-link:hover{
    color: #409eff;
    .el-dropdown-icon {
        transform: rotate(180deg);
    }
}

.username {
    margin: 5px;
}

.el-tooltip__trigger:focus {
    outline: none;
}

.not-login {
    cursor: pointer;
    display: flex;
    align-items: center;
}

.not-login:hover {
    color: #409eff;
}

.not-login span {
    margin: 5px;
}
</style>