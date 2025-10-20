<template>
    <div class="profile-page">
        <NavBar />

        <div class="container">
            <!-- 个人信息卡片 -->
            <el-card class="profile-card">
                <div class="profile-header">
                    <el-avatar class="avatar">
                        <img :src="userInfo.avatar" alt="用户头像">
                    </el-avatar>

                    <div class="user-info">
                        <h2>{{ userInfo.username }}</h2>
                        <div class="user-meta">
                            <span class="credit-score">信用分: {{ userInfo.credit_score }}</span>
                            <span class="join-date">注册时间: {{ formatDate }}</span>
                        </div>
                    </div>

                    <el-button type="primary" @click="showEditDialog = true">
                        编辑资料
                    </el-button>
                </div>

                <el-divider />

                <div class="profile-details">
                    <div class="detail-item">
                        <span class="label">邮箱:</span>
                        <span>{{ userInfo.email || '未设置' }}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">手机号:</span>
                        <span>{{ userInfo.phone || '未设置' }}</span>
                    </div>
                </div>
            </el-card>

            <!-- 发布的物品列表 -->
            <div class="items-section">
                <h3>发布的物品</h3>
                <div class="items-grid">
                    <ItemCard 
                        v-for="item in items"
                        :item="item"
                        :key="item.id"
                        @click="goToDetail(item.id)"
                    />
                </div>

                <div v-if="items.length === 0 && !loading" class="empty-state">
                    <el-empty description="暂无发布的物品" />
                </div>
            </div>
        </div>

        <!-- 编辑资料对话框 -->
        <el-dialog
            title="编辑个人资料"
            v-model="showEditDialog"
            width="500px"
        >
            <el-form
                ref="form"
                :rules="rules"
                :model="editForm"
                label-width="60px"
            >
                <el-form-item label="用户名:">
                    <el-input v-model="editForm.username"></el-input>
                </el-form-item>
                <el-form-item label="邮箱:">
                    <el-input v-model="editForm.email"></el-input>
                </el-form-item>
                <el-form-item label="电话:">
                    <el-input v-model="editForm.phone"></el-input>
                </el-form-item>
                <el-form-item label="头像:">
                    <el-upload
                        class="avatar-uploader"
                        :action="`${baseURL}/items/upload-image`"
                        :on-success="handleImageSuccess"
                        list-type="picture-card"
                        :limit="1"
                    >
                        <!-- <img 
                            v-if="userInfo.avatar"
                            :src="editForm.avatar"
                            class="avatar"
                        /> -->
                        <el-icon class="avatar-uploader-icon">
                            <Plus />
                        </el-icon>
                    </el-upload>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showEditDialog = false">取消</el-button>
                <el-button type="primary" @click="submitEditForm">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, updateCurrentUser } from '@/api/user';
import { readMyItems } from '@/api/item';
import { dayjs } from 'element-plus';
import { Plus } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue';
import ItemCard from '@/components/ItemCard.vue';
import { baseURL, baseImgURL } from '@/utils/request';

const userInfo = ref({})
const showEditDialog = ref(false)
const items = ref([])
const router = useRouter()
const loading = ref(false)
const editForm = ref({
    username: '',
    email: '',
    phone: '',
    avatar: ''
})

const formatDate = computed(() => {
    return dayjs(userInfo.value.created_at).format("YYYY/MM/DD HH:mm:ss")
})

const goToDetail = (id) => {
    router.push(`/items/${id}`)
}

const fetchUserInfo = async () => {
    try {
        loading.value = true
        const data = await getCurrentUser()
        userInfo.value = data
        // console.log(userInfo.value)
        editForm.value = {
            username: data.username,
            email: data.email,
            phone: data.phone,
            avatar: data.avatar
        }
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

const fetchMyItem = async () => {
    try {
        const data = await readMyItems()
        items.value = data
        console.log(items.value)
    } catch (error) {
        console.error(error)
    }
}

const handleImageSuccess = (response) => {
    editForm.value.avatar = `${baseImgURL}/${response.file_name}`
    console.log(editForm.value)
}

const submitEditForm = async () => {
    try {
        await updateCurrentUser(editForm.value)
        showEditDialog.value = false
        router.go(0)
        ElMessage.success('修改成功')
    } catch (error) {
        console.error(error)
    }
}

onMounted(() => {
    fetchUserInfo()
    fetchMyItem()
})
</script>

<style scoped>
.profile-page {
    background: #f5f7fa;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 20px;
}

.profile-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.avatar {
    width: 120px;
    height: 120px;
    margin-right: 20px;
}

.user-info {
    flex: 1;
}

.user-meta {
    margin-top: 10px;
    display: flex;
    gap: 20px;
    color: #666;
}

.credit-score {
    color: #409eff
}

.profile-details {
    margin-top: 10px;
}

.detail-item {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.label {
    width: 80px;
    color: #666;
}

.items-section {
    margin-top: 30px;
}

.items-grid {
    display: flex;
    flex-wrap: wrap;
    margin-top: 20px;
}

.empty-state {
    text-align: center;
    padding: 40px 0;
}

.avatar-uploader{
    /* width: 120px;
    height: 120px; */
}

.avatar-uploader-icon {
    /* font-size: 28px;
    color: #8c939d;
    border: 1px dashed #d9d9d9;
    width: 120px;
    height: 120px; */
}
</style>