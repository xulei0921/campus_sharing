<template>
    <div class="item-card">
        <div class="item-image">
            <el-image
                :src="item.images[0] || `https://picsum.photos/id/${Math.floor(Math.random() * (1001))}/400/300`"
                fit="cover"
            ></el-image>
            <el-tag
                v-if="item.status == 'sold'"
                class="sold-tag"
                type="danger"
            >
                已交易
            </el-tag>
            <el-tag
                v-else-if="item.status == 'available'"
                class="available-tag"
                type="success"
            >
                可交易
            </el-tag>
            <el-tag
                v-else
                class="trading-tag"
                type="info"
            >
                交易中
            </el-tag>
        </div>
        <div class="item-info">
            <h3 class="item-title">{{ item.title }}</h3>
            <p class="item-price">￥{{ item.price }}</p>
            <div class="item-meta">
                <div class="category">{{ `分类:${category_detail.name}` }}</div>
                <div class="time">{{ `发布于 ${formatTime(item.created_at)}` }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, onMounted, ref } from 'vue';
import { getCategoryById } from '@/api/categories';

const category_detail = ref('')

const props = defineProps({
    item: {
        type: Object,
        required: true,
        default: () => ({})
    }
})

const currentItem = props.item

// 格式化时间为相对时间
const formatTime = (timeString) => {
    const now = new Date()
    const past = new Date(timeString)
    const diffMs = now - past
    const diffMins = Math.floor(diffMs / 1000 / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 60) {
        return `${diffMins} 分钟前`
    } else if (diffHours < 24) {
        return `${diffHours} 小时前`
    } else if(diffDays < 30) {
        return `${diffDays} 天前`
    } else {
        return past.toLocaleDateString()
    }
}

const fetchCategory = async () => {
    try {
        const data = await getCategoryById(currentItem.category_id)
        category_detail.value = data
    } catch (error) {
        ElMessage.error("获取分类数据失败")
        console.error(error)
    }
}

onMounted(() => {
    fetchCategory()
})
</script>

<style scoped>
.item-card {
    width: 240px;
    height: 380px;
    /* background: saddlebrown; */
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-right: 30px;
}

.item-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.item-image {
    position: relative;
    height: 240px;
    width: 240px;
    /* background-color: skyblue; */
}

.sold-tag {
    position: absolute;
    bottom: -40px;
    right: 10px;
}

.available-tag {
    position: absolute;
    bottom: -40px;
    right: 10px;
}

.trading-tag {
    position: absolute;
    bottom: -40px;
    right: 10px;
}

.item-image .el-image {
    width: 100%;
    height: 100%;
}

.item-info {
    width: 100%;
    height: 200%;
    /* background-color: red; */
}

.item-title {
    margin: 0;
    padding: 15px 10px 5px;
}

.item-price {
    margin: 0;
    padding: 0 10px;
    color: #FF4F24;
    font-weight: 800;
    font-size: 24px;
}

.item-meta {
    /* display: block; */
}

.item-meta .category {
    margin: 5px 0;
    padding: 0 10px;
    font-size: 14px;
}

.item-meta .time {
    margin: 0;
    padding: 0 10px;
    font-size: 13px;
    color: #999999;
}
</style>