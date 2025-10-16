<template>
    <el-dialog
        title="发起交易"
        :model-value="visible"
        :before-close="handleClose"
        destroy-on-close
    >
        <el-form
            :model="formModel"
            :rules="rules"
            ref="form"
        >
            <el-form-item label="交易时间" prop="meeting_time">
                <el-date-picker
                    v-model="formModel.meeting_time"
                    type="datetime"
                    placeholder="请选择交易时间"
                    format="YYYY/MM/DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    @change="handleChange"
                ></el-date-picker>
            </el-form-item>
            <el-form-item label="交易地点" prop="meeting_location">
                <el-input
                    v-model="formModel.meeting_location"
                    placeholder="请输入交易地点"
                ></el-input>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="handleClose">取消</el-button>
            <el-button type="primary" @click="handleSubmit">确认发起</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { createTransaction } from '@/api/transactions'

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    item_id: {
        type: [String, Number],
        required: true
    }
})

const form = ref('')
const formModel = ref({
    meeting_time: '',
    meeting_location: '',
    item_id: Number(props.item_id)
})

const rules = {
    meeting_time: [
        { required: true, message: '请选择交易时间', trigger: 'blur' }
    ],
    meeting_location: [
        { required: true, message: '请输入交易地点', trigger: 'blur' }
    ]
}

const emit = defineEmits(['update:visible', 'close'])

const handleClose = () => {
    emit('update:visible', false)
    emit('close')
}

const handleChange = () => {
    console.log(formModel.value)
}

const handleSubmit = async () => {
    try {
        await form.value.validate()
        await createTransaction(formModel.value)
        ElMessage.success("成功发起交易")
    } catch (error) {
        console.error(error)
    }
}
</script>

<style scoped>

</style>