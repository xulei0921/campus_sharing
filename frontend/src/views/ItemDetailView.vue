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
                        <div class="form-title">
                            <h1 class="title">{{ item.title }}</h1>
                            <el-icon 
                                :size="20"
                                class="edit-icon"
                                @click="openEditForm"
                                v-show="currentUserId == item.owner.id"
                            >
                                <Edit />
                            </el-icon>

                            <div v-show="item.owner.id !== currentUserId && item.status === 'available'">
                                <el-icon
                                    v-if="!isFavorited"
                                    :size="20"
                                    class="favorite-icon"
                                    @click="addFavorite"
                                >
                                    <Star />
                                </el-icon>
                                <el-icon
                                    v-else
                                    :size="20"
                                    class="favorite-icon"
                                    @click="removeFavorite"
                                    color="#FFD54D"
                                >
                                    <StarFilled />
                                </el-icon>
                            </div>

                            <el-dialog
                                title="编辑物品"
                                v-model="showEditForm"
                                width="800px"
                            >
                                <el-form
                                    ref="form"
                                    :rules="rules"
                                    :model="formModel"
                                    label-width="80px"
                                >
                                    <el-form-item label="物品标题">
                                        <el-input v-model="formModel.title"></el-input>
                                    </el-form-item>
                                    <el-form-item label="物品描述">
                                        <el-input
                                            v-model="formModel.description"
                                            type="textarea"
                                            rows="3"
                                        ></el-input>
                                    </el-form-item>
                                    <el-form-item label="物品价格">
                                        <el-input-number
                                            v-model="formModel.price"
                                            :min="0"
                                        >
                                            <template #prefix>
                                                <span>￥</span>
                                            </template>
                                        </el-input-number>
                                    </el-form-item>
                                    <el-form-item label="物品分类">
                                        <el-select v-model="formModel.category_id" placeholder="请选择分类">
                                            <el-option
                                                v-for="category in categories"
                                                :key="category.id"
                                                :label="category.name"
                                                :value="category.id"
                                            ></el-option>
                                        </el-select>
                                    </el-form-item>
                                    <el-form-item label="物品状态">
                                        <el-select v-model="formModel.status" placeholder="请选择物品状态">
                                            <el-option value="available" label="可交易">可交易</el-option>
                                            <el-option value="trading" label="交易中">交易中</el-option>
                                            <el-option value="sold" label="已交易">已交易</el-option>
                                        </el-select>
                                    </el-form-item>
                                    <el-form-item label="交易地点">
                                        <el-input
                                            v-model="formModel.location"
                                            placeholder="请输入交易地点"
                                        ></el-input>
                                    </el-form-item>
                                    <el-form-item label="物品图片">
                                        <el-upload
                                            :action="`${baseURL}/items/upload-image`"
                                            multiple
                                            :on-success="handleImageSuccess"
                                            list-type="picture-card"
                                            :limit="3"
                                        >
                                            <el-icon>
                                                <Plus />
                                            </el-icon>
                                        </el-upload>
                                        <div class="upload-hint">最多上传3张图片，支持jpg、png格式</div>
                                    </el-form-item>
                                </el-form>

                                <template #footer>
                                    <el-button @click="showEditForm = false">取消</el-button>
                                    <el-button type="primary" @click="submitEditForm">保存</el-button>
                                </template>
                            </el-dialog>
                        </div>
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
                                :disabled="item.status !== 'available' || !isLogin() || currentUserId == item.owner.id"
                            >
                                联系卖家
                            </el-button>
                            <el-button
                                type="success"
                                size="large"
                                @click="handleCreateTransaction"
                                :disabled="item.status !== 'available' || !isLogin() || currentUserId == item.owner.id"
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
import { getItemById, updateItem } from '@/api/item';
import { getCurrentUser } from '@/api/user'
import { getAllCategories } from '@/api/categories'
import { checkItemFavorited, createFavorite, deleteFavorite } from '@/api/favorites';
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { dayjs } from 'element-plus';
import { Edit, Loading, Plus, Star, StarFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores';
import { baseURL } from '@/utils/request';

const userStore = useUserStore()

const { isLogin } = userStore

const route = useRoute()
const router = useRouter()
const itemId = route.params.id
const item = ref({})
const isLoading = ref(true)
const showTransactionForm = ref(false)
const showEditForm = ref(false)
const currentUserId = ref(null)
const categories = ref([])
const isFavorited = ref(false)

const formModel = ref({
    title: "",
    description: "",
    price: null,
    category_id: null,
    status: "",
    location: "",
    images: []
})

const openEditForm = () => {
    showEditForm.value = true
    fetchCategories()
    formModel.value = {
        title: item.value.title,
        description: item.value.description,
        price: item.value.price,
        category_id: item.value.category_id,
        status: item.value.status,
        location: item.value.location,
        images: []
    }
    // console.log(formModel.value)
}

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

const fetchCurrentUserId = async () => {
    try {
        const data = await getCurrentUser()
        currentUserId.value = data.id
    } catch (error) {
        console.error(error)
    }
}

const fetchCategories = async () => {
    try {
        const data = await getAllCategories()
        categories.value = data
    } catch (error) {
        console.error(error)
    }
}

const fetchItemFavorited = async () => {
    try {
        const data = await checkItemFavorited(itemId)
        isFavorited.value = data.is_favorited
    } catch (error) {
        console.error(error)
    }
}

const handleCreateTransaction = () => {
    showTransactionForm.value = true
} 

const handleImageSuccess = (response) => {
    formModel.value.images.push(response.file_name)
    console.log(formModel.value)
}

const formattedTime = computed(() => {
    return dayjs(item.value.created_at).format("YYYY-MM-DD HH:mm:ss")
})

const submitEditForm = async () => {
    formModel.value.images = formModel.value.images.map(fileName => ({
        image_url: fileName
    }))

    try {
        await updateItem(item.value.id, formModel.value)
        ElMessage.success('修改物品信息成功')
        showEditForm.value = false
        router.go(0)
    } catch (error) {
        console.error(error)
    }
}

const addFavorite = async () => {
    try {
        await createFavorite(item.value.id)
        ElMessage.success("物品收藏成功")
        // router.go(0)
        isFavorited.value = true
    } catch (error) {
        console.error(error)
    }
}

const removeFavorite = async () => {
    try {
        await deleteFavorite(item.value.id)
        ElMessage.error("取消收藏成功")
        // router.go(0)
        isFavorited.value = false
    } catch (error) {
        console.error(error)
    }
}

onMounted(() => {
    fetchItemDetail(itemId)
    if (isLogin()) {
        fetchCurrentUserId()
        fetchItemFavorited()
    }
    // console.log(itemId)
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

.form-title {
    display: flex;
    align-items: center;
}

.title {
    margin-right: 15px;
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

.edit-icon {
    cursor: pointer;
}

.edit-icon:hover {
    color: #409eff;
}

.upload-hint {
    margin-left: 15px;
}

.favorite-icon {
    margin-left: 15px;
    cursor: pointer;
}
</style>