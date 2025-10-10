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
                <el-avatar @click="$router.push('/profile')" class="avatar">
                    <img src="https://picsum.photos/200/200" alt="用户头像">
                </el-avatar>
            </div>
        </div>
    </el-header>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute()

const activePath = computed(() => {
    return route.path
})

const handleSelect = (index) => {
    window.location.href = index
}
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
    /* max-width: 1200px; */
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
</style>