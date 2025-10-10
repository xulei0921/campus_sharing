<template>
    <div class="home-container">
        <!-- 导航栏 -->
        <nav-bar />
        首页
        <!-- 搜索区域 -->
        <!-- <div class="search-container">
            <div class="search-box">
                <input 
                  type="text"
                  v-model="searchQuery"
                  placeholder="搜索闲置物品..."
                >
            </div>
        </div> -->
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue'
</script>