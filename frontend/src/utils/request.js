import axios from "axios";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import router from "@/router";
import { useUserStore } from "@/stores";

// const baseURL = 'http://127.0.0.1:8000/api'
const baseURL = '/api'

const instance = axios.create({
    // TODO 1. 基础地址，超时时间
    baseURL,
    timeout: 5000
})

// 请求拦截器
instance.interceptors.request.use(
    (config) => {
        // TODO 2. 携带token
        const userStore = useUserStore()
        if (userStore.token) {
            config.headers.Authorization = userStore.token
        }
        return config
    },
    (err) => Promise.reject(err)
)

// 响应拦截器
instance.interceptors.response.use(
    (res) => {
        // TODO 3. 处理业务失败
        // TODO 4. 摘取核心响应数据
        // if (res.data.code === 0) {
        //     return res
        // }
        // 处理业务失败，给错误提示，抛出错误
        // ElMessage.error({ message: res.response.data.detail || '服务异常', type: 'error' })
        // return Promise.reject(res.response.data.detail)
        return res.data
    },
    (err) => {
        // TODO 5. 处理401错误
        // 错误的特殊情况 => 401 权限不足 或 token 过期 => 拦截到登录
        if (err.response?.status === 401) {
            router.push('/login')
            ElMessage.error({ message: err.response?.data?.detail } || '请求失败，请稍后重试')
            return Promise.reject(err.response?.data?.detail || '请求失败')
        }

        // 错误的默认情况 => 只要给提示
        const errorMsg = err.response?.data?.detail || '请求失败，请稍后重试'
        ElMessage.error(errorMsg)
        // console.log(err)
        return Promise.reject(errorMsg)
    }
)

export default instance
export { baseURL }
