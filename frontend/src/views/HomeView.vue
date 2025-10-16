<template>
    <div class="home-page">
        <!-- 导航栏 -->
        <nav-bar />
        
        <!-- 搜索和筛选区域 -->
        <div class="filter-container">
            <div class="filter-options">
                <el-select
                    v-model="selectedCategory"
                    placeholder="全部分类"
                    clearable
                    @change="handleFilterChange"
                    class="category-select"
                >
                    <el-option
                        v-for="category in categories"
                        :key="category.id"
                        :label="category.name"
                        :value="category.id"
                    ></el-option>
                </el-select>
            </div>

            <div class="search-box">
                <el-input
                    v-model="searchKeyword"
                    placeholder="搜索物品名称或描述..."
                    clearable
                    @keyup.enter="handleSearch"
                >
                    <template #append>
                        <el-button :icon="Search" @click="handleSearch"></el-button>
                    </template>
                </el-input>
            </div>
        </div>

        <!-- 物品列表 -->
        <div class="items-container">
            <div class="items-grid">
                <item-card
                    v-for="item in items"
                    :item="item"
                    :key="item.id"
                    @click="goToDetail(item.id)"
                ></item-card>
            </div>

            <!-- 空状态 -->
            <div v-if="items.length === 0 && !loading" class="empty-state">
                <el-empty description="暂无物品数据" />
            </div>

            <!-- 加载中 -->
            <div v-if="loading" class="loading-state" v-loading="loading">
                <p>加载中...</p>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllCategories } from '@/api/categories'
import { getItems } from '@/api/item'
import { Search } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import ItemCard from '@/components/ItemCard.vue'

const searchKeyword = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const categories = ref([])
const items = ref([])
const pageSize = ref(5)
const router = useRouter()

onMounted(() => {
    fetchCategories()
    fetchItems()
})

const handleSearch = () => {
    fetchItems()
}

const handleFilterChange = () => {
    fetchItems()
}

const goToDetail = (id) => {
    // console.log(id)
    router.push(`/items/${id}`)
}

const fetchCategories = async () => {
    try {
        const data = await getAllCategories()
        categories.value = data
    } catch (error) {
        ElMessage.error('获取分类失败')
        console.error(error)
    }
}

const fetchItems = async () => {
    try {
        loading.value = true
        const params = {
            // page: currentPage.value,
            limit: pageSize.value,
            search: searchKeyword.value || undefined,
            category_id: selectedCategory.value || undefined,
        }

        const resp = await getItems(params)
        console.log(resp)
        items.value = resp

    } catch (error) {
        ElMessage.error('获取物品失败')
        console.error(error)
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.home-page {
    background-color: #f5f7fa;
    min-height: 100vh;
}

/* 筛选区域样式 */
.filter-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    display: flex;
}

.search-box {
    width: 300px;
    margin-bottom: 15px;
    margin-left: 15px;
}

.search-box .el-input {
    width: 100%;
    max-width: 800px;
}

.filter-options {
    /* display: flex; */
    /* gap: 15px; */
}

.category-select {
    width: 160px;
}

.items-container {
    max-width: 1200px;
    margin: 0 auto;
} 

.items-grid {
    display: flex;
    /* justify-content: space-between; */
    flex-wrap: wrap;
}
</style>