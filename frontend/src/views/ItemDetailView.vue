<template>
    <div class="item-detail">
        <NavBar />

        <div class="container">

            <div v-if="isLoading" class="loading">加载中...</div>

            <el-row :gutter="20" v-else>
                <el-col :span="12">
                    <el-carousel v-if="item.images" class="custom-carousel">
                        <el-carousel-item v-for="img in item.images">
                            <div class="carousel-img-container">
                                <el-image
                                    class="item-image"
                                    :src="img?.image_url"
                                    fit="contain"
                                ></el-image>
                            </div>
                        </el-carousel-item>
                    </el-carousel>
                    <div v-else class="no-image">暂无图片</div>
                </el-col>

                <el-col :span="12">
                    <div class="item-info">
                        <h1 class="title">{{ item.title }}</h1>
                        <div class="price">￥ {{ item.price }}</div>

                        <el-divider />

                        <div class="details">
                            <p><span class="label">物品描述:</span>{{ item.description }}</p>
                            <p><span class="label">物品分类:</span>{{ item.category.name }}</p>
                            <p><span class="label">发布时间:</span>{{ formattedTime }}</p>
                            <p><span class="label">卖家推荐交易地点:</span>{{ item.location }}</p>
                            <p class="status-tag"><span class="label">状态: </span>
                                <el-tag v-if="item.status === 'available'" type="success">
                                    可交易
                                </el-tag>
                                <el-tag v-else-if="item.status === 'sold'" type="danger">
                                    已交易
                                </el-tag>
                                <el-tag v-else type="info">
                                    交易中
                                </el-tag>
                            </p>
                        </div>

                        <el-divider />

                        <div class="seller-info">
                            <h3>卖家信息</h3>
                            <div class="seller" @click="$router.push(`/user/${item.owner.id}`)">
                                <el-avatar>
                                    <img :src="item.owner.avatar" alt="">
                                </el-avatar>
                                <div class="seller-name">{{ item.owner.username }}</div>
                            </div>
                        </div>

                        <div class="actions">
                            <el-button
                                type="primary"
                                size="large"
                                @click="handleContact"
                                :disabled="item.status !== 'available'"
                            >
                                联系卖家
                            </el-button>
                            <el-button
                                type="success"
                                size="large"
                                @click="handleCreateTransaction"
                                :disabled="item.status !== 'available'"
                            >
                                发起交易
                            </el-button>
                        </div>
                    </div>
                </el-col>
            </el-row>

            <TransactionForm
                v-model:visible="showTransactionForm"
                :item_id="itemId"
            />

        </div>
    </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
import TransactionForm from '@/components/TransactionForm.vue';
import { getItemById } from '@/api/item';
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { dayjs } from 'element-plus';

const route = useRoute()
const router = useRouter()
const itemId = route.params.id
const item = ref({})
const isLoading = ref(true)
const showTransactionForm = ref(false)

const fetchItemDetail = async (itemId) => {
    try {
        isLoading.value = true
        const data = await getItemById(itemId)
        item.value = data
    } catch(error) {
        ElMessage.error('获取物品详情失败!')
        console.error(error)
    } finally {
        isLoading.value = false
    }
}

const handleCreateTransaction = () => {
    showTransactionForm.value = true
}

const formattedTime = computed(() => {
    return dayjs(item.value.created_at).format("YYYY-MM-DD HH:mm:ss")
})

onMounted(() => {
    // console.log(itemId)
    fetchItemDetail(itemId)
    console.log(item)
})
</script>

<style scoped>
.item-detail {
    min-height: 100vh;
    background: #f5f7fa;
}

.container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 20px;
}

.carousel-img-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fff;
}

.item-image {
    width: 100%;
    height: 100%;
    background-color: #fff;
    /* padding: 20px; */
    border-radius: 4px;
}

.label {
    margin-right: 10px;
    font-weight: bold;
}

.seller {
    cursor: pointer;
    display: flex;
    align-items: center;
}

.seller-name {
    margin-left: 10px;
}

.status-tag {
    display: flex;
    align-items: center;
}

.custom-carousel {
    width: 60%;
    margin: 100px auto;
}

.actions {
    margin-top: 20px;
    display: flex;
}
</style>