<template>
    <div class="create-item">
        <nav-bar />
        <div class="container">
            <h1>发布闲置物品</h1>

            <el-form
                ref="form"
                :model="formModel"
                :rules="rules"
                label-width="120px"
                class="create-form custom-form"
            >
                <el-form-item label="物品标题" prop="title">
                    <el-input v-model="formModel.title" placeholder="请输入物品标题"></el-input>
                </el-form-item>

                <el-form-item label="物品分类" prop="category_id">
                    <el-select v-model="formModel.category_id" placeholder="请选择分类">
                        <el-option
                            v-for="category in categories"
                            :key="category.id"
                            :label="category.name"
                            :value="category.id"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="物品价格" prop="price">
                    <el-input-number
                        v-model="formModel.price"
                        :min="0"
                    >
                        <template #prefix>
                            <span>￥</span>
                        </template>
                    </el-input-number>
                </el-form-item>

                <el-form-item label="交易地点" prop="location">
                    <el-input
                        v-model="formModel.location"
                        placeholder="请输入交易地点"
                    ></el-input>
                </el-form-item>

                <el-form-item label="物品图片" prop="images">
                    <el-upload
                        class="upload"
                        :action="`${baseURL}/items/upload-image`"
                        multiple
                        :on-success="handleImageSuccess"
                        :limit="3"
                        :file-list="fileList"
                        list-type="picture-card"
                    >
                        <el-button type="primary">点击上传</el-button>
                    </el-upload>
                    <div class="upload-hint">最多上传3张图片，支持jpg、png格式</div>
                </el-form-item>

                <el-form-item label="物品描述" prop="description">
                    <el-input
                        v-model="formModel.description"
                        type="textarea"
                        rows="5"
                        placeholder="请详细描述物品情况，新旧程度等"
                    ></el-input>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="submitForm">发布</el-button>
                    <el-button @click="resetForm">重置</el-button>
                </el-form-item>
            </el-form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import { getAllCategories } from '@/api/categories';
import { createItem, uploadItemImages } from '@/api/item';
import { Money } from '@element-plus/icons-vue'
import { baseURL } from '@/utils/request';

const formModel = ref({
    title: '',
    description: '',
    price: null,
    category_id: null,
    location: '',
    images: []
})

const rules = {
    title: [
        { required: true, message: '请输入物品标题', trigger: 'blur' }
    ],
    category_id: [
        { required: true, message: '请选择物品分类', trigger: 'change' }
    ],
    price: [
        { required: true, message: '请输入价格', trigger: 'blur' },
        { type: 'number', min: 0, message: '价格必须>=0', trigger: 'blur' }
    ],
    location: [
        { required: true, message: '请输入交易地点', trigger: 'blur' }
    ],
    images: [
        { required: false }
    ],
    description: [
        { required: true, message: '请输入描述', trigger: 'blur' }
    ]
}

const categories = ref([])
const fileList = ref([])
const form = ref(null)

const fetchCategories = async () => {
    try {
        const data = await getAllCategories()
        categories.value = data
    } catch (error) {
        ElMessage.error("获取分类失败")
        console.error(error)
    }
}

const handleImageSuccess = (response) => {
    formModel.value.images.push(response.file_name)
    console.log(formModel)
}

// 提交表单数据
const submitForm = async () => {
    formModel.value.images = formModel.value.images.map(fileName => ({
        image_url: fileName
    }))

    try {
        console.log(formModel.value)
        await form.value.validate()
        await createItem(formModel.value)
        ElMessage.success("发布物品成功")
    } catch (error) {
        console.error(error)
    }
}

// 重置表单
const resetForm = () => {
    form.value.resetFields()
}

onMounted(() => {
    fetchCategories()
})

</script>

<style scoped>
.create-item {
    background: #f5f7fa;
    min-height: 100vh;
}

.container {
    min-width: 800px;
    margin: 20px auto;
    padding: 0 20px;
}

.create-form {
    background-color: #fff;
    padding: 20px;
    border-radius: 20px;
    margin-top: 20px;
}

.custom-form :deep(.el-input),
.custom-form :deep(.el-select),
.custom-form :deep(.el-textarea){
    width: 300px;
}

.custom-form :deep(.el-input-number) {
    width: 180px;
}

.upload {
    margin-top: 10px;
}

.upload-hint {
    margin-left: 15px;
}

</style>