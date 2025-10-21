<template>
<div class="transactions-page">
    <NavBar />

    <div class="container">
        <h2>我的所有交易</h2>

        <!-- 交易类型切换 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="我买到的" name="buy"></el-tab-pane>
            <el-tab-pane label="我卖出的" name="sell"></el-tab-pane>
        </el-tabs>

        <!-- 交易列表 -->
        <div class="transactions-list">
            <el-card
                v-for="transaction in transactions"
                :key="transaction.id"
                class="transaction-card"
            >
                <div class="transaction-header">
                    <div class="transaction-info">
                        <h3 class="item-title">{{ transaction.item.title }}</h3>
                        <div class="transaction-meta">
                            <span>交易ID: {{ transaction.id }}</span>
                            <span>创建时间: {{ formatDate(transaction.created_at) }}</span>
                        </div>
                    </div>

                    <el-tag
                        :type="getStatusTagType(transaction.status)"
                        class="status-tag"
                    >
                        {{ getStatusText(transaction.status) }}
                    </el-tag>
                </div>

                <el-divider />

                <div class="transaction-details">
                    <div class="detail-row">
                        <span class="detail-label">
                            {{ activeTab === 'buy' ? '卖家' : '买家' }}:
                        </span>
                        <span>
                            {{ activeTab === 'buy' ? transaction.seller.username : transaction.buyer.username }}
                        </span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">交易时间:</span>
                        <span>{{ formatDate(transaction.meeting_time) }}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">交易地点:</span>
                        <span>{{ transaction.meeting_location }}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">物品价格:</span>
                        <span>￥{{ transaction.item.price }}</span>
                    </div>
                    <!-- <button @click="canReview(transaction)">测试评价</button> -->
                </div>

                <div class="transaction-actions">
                    <el-button
                        v-if="canConfirm(transaction)"
                        type="primary"
                        @click="handleConfirm(transaction.id)"
                    >
                        确认交易
                    </el-button>

                    <el-button
                        v-if="canComplete(transaction)"
                        type="success"
                        @click="handleComplete(transaction.id)"
                    >
                        完成交易
                    </el-button>

                    <el-button
                        v-if="canCancel(transaction)"
                        type="danger"
                        @click="handleCancel(transaction)"
                    >
                        取消交易
                    </el-button>

                    <el-button
                        v-if="canReview(transaction)"
                        type="info"
                        @click="handleReview(transaction)"
                    >
                        评价对方
                    </el-button>
                </div>
            </el-card>

            <!-- 空状态 -->
            <div v-if="transactions.length === 0 && !loading" class="empty-state">
                <el-empty description="暂无相关交易记录"></el-empty>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="loading-state">
                <el-loading :visible="loading" text="加载中..." />
            </div>
        </div>
    </div>

    <!-- 评价对话框 -->
    <el-dialog
        title="评价交易"
        v-model="showReviewDialog"
        width="500px"
    >
        <el-form
            ref="form"
            :rules="rules"
            :model="reviewForm"
            label-width="80px"
        >
            <el-form-item label="评分:" prop="rating">
                <el-rate
                    v-model="reviewForm.rating"
                    :max="5"
                    clearable
                ></el-rate>
            </el-form-item>
            <el-form-item label="评价内容:" prop="comment">
                <el-input
                    v-model="reviewForm.comment"
                    type="textarea"
                    rows="4"
                    placeholder="请输入评价内容"
                ></el-input>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="showReviewDialog = false">取消</el-button>
            <el-button type="primary" @click="submitReview">提交评价</el-button>
        </template>
    </el-dialog>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import { getCurrentUserBuyTransactions, getCurrentUserSellTransactions, updateTransaction } from '@/api/transactions';
import { getCurrentUser } from '@/api/user';
import { createReview } from '@/api/reviews';

const activeTab = ref('buy')
const transactions = ref([])
const loading = ref(false)
const currentUserId = ref(null)
const showReviewDialog = ref(false)
const form = ref()
const reviewForm = ref({
    rating: 0,
    comment: '',
    transaction_id: null,
    reviewee_id: null
})

const rules = {
    rating: [
        { required: true, message: '请给出评分', trigger: 'change' },
        { min: 1, message: '评分不能低于1分', trigger: 'change' }
    ]
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

// 获取交易状态显示文本
const getStatusText = (status) => {
    const statusMap = {
        'pending': '待确认',
        'confirmed': '已确认',
        'completed': '已完成',
        'cancelled': '已取消'
    }
    return statusMap[status] || status
}

// 获取交易状态标签样式
const getStatusTagType = (status) => {
    const typeMap = {
        'pending': 'warning',
        'confirmed': 'info',
        'completed': 'success',
        'cancelled': 'danger'
    }
    return typeMap[status] || 'default'
}

// 判断是否可以确认交易（卖家对pending状态）
const canConfirm = (transaction) => {
    return activeTab.value === 'sell' && transaction.status === 'pending'
}

// 判断是否可以完成交易（双方对confirmed状态）
const canComplete = (transaction) => {
    // console.log(transaction.status === 'confirmed')
    return transaction.status === 'confirmed'
}

// 判断是否可以取消交易（未完成状态）
const canCancel = (transaction) => {
    return ['pending', 'confirm'].includes(transaction.status)
}

// 判断是否可以评价（交易完成且未评价）
const canReview = (transaction) => {

    // console.log(transaction.reviews)
    // console.log(transaction.reviews[0]?.reviewer_id)

    if (transaction.status === 'completed') {
        if (transaction.reviews.length === 0) {
            // console.log("当前交易没有任何评价")
            return true
        } else if (transaction.reviews.length === 1 && transaction.reviews[0].reviewer_id !== currentUserId.value) {
            // console.log("当前交易只有对方给出评价")
            return true
        } else {
            // console.log('当前用户已评价')
            return false
        }
    } else {
        // console.log("当前交易未完成")
        return false
    }
}

const handleTabChange = () => {
    fetchTransactions()
}

const handleConfirm = async (transaction_id) => {
    try {
        await updateTransaction(transaction_id, { status: "confirmed" })
        ElMessage.success('交易已确认')
        fetchTransactions()
    } catch (error) {
        console.error(error)
    }
}

const handleComplete = async (transaction_id) => {
    try {
        await updateTransaction(transaction_id, { status: "completed" })
        ElMessage.success('交易已完成')
        fetchTransactions()
    } catch (error) {
        console.error(error)
    }
}

const handleCancel = async (transaction_id) => {
    try {
        await updateTransaction(transaction_id, { status: "cancelled" })
        ElMessage.error('交易已取消')
        fetchTransactions()
    } catch (error) {
        console.error(error)
    }
}

const handleReview = async (transaction) => {
    showReviewDialog.value = true
    reviewForm.value = {
        rating: 0,
        comment: '',
        transaction_id: transaction.id,
        reviewee_id: activeTab.value === 'buy' ? transaction.seller_id : transaction.buyer_id
    }
    // console.log(reviewForm.value)
}

const submitReview = async () => {
    try {
        await form.value.validate()
        await createReview(reviewForm.value)
        ElMessage.success('评价成功')
        showReviewDialog.value = false
        fetchTransactions()
    } catch (error) {
        console.error(error)
    }
}

const fetchTransactions = async () => {
    try {
        loading.value = true
        let data
        if (activeTab.value === 'buy') {
            data = await getCurrentUserBuyTransactions()
        } else {
            data = await getCurrentUserSellTransactions()
        }
        transactions.value = data
    } catch (error) {
        ElMessage.error('获取交易列表失败')
        console.error(error)
    } finally {
        loading.value = false
    }
}

const fetchCurrentUser = async () => {
    try {
        loading.value = true
        const data = await getCurrentUser()
        currentUserId.value = data.id
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchCurrentUser()
    fetchTransactions()
})
</script>

<style scoped>
.transactions-page {
    background: #f5f7fa;
    min-height: 100vh;
    padding-bottom: 40px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.transaction-tabs {
    margin: 20px 0;
    background-color: #fff;
    padding: 10px;
    border-radius: 4px;
}

.transactions-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.transaction-card {
    transition: all 0.3s ease;
}

.transaction-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.transaction-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.item-title {
    margin: 0;
    color: #333;
    font-size: 18px;
    cursor: pointer;
}

.item-title:hover {
    color: #409eff;
}

.transaction-meta {
    display: flex;
    gap: 15px;
    color: #666;
    font-size: 14px;
    margin-top: 5px;
}

.status-tag {
    margin-top: 5px;
}

.transaction-details {
    margin: 15px 0;
}

.detail-row {
    margin-bottom: 8px;
    display: flex;
    line-height: 1.6;
}

.detail-label {
    width: 100px;
    color: #666;
    font-weight: 500;
}

.transaction-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 15px;
}

.empty-state {
    text-align: center;
    padding: 60px 0;
    background-color: #fff;
    border-radius: 4px;
}

.loading-state {
    padding: 60px 0;
    text-align: center;
    background: #fff;
    border-radius: 4px;
}
</style>