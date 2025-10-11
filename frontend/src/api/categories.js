import request from '@/utils/request'

// 创建新分类
export const createCategory = ({ name, description }) => {
    return request.post('/categories', { name, description })
}

// 获取所有分类列表
export const getAllCategories = () => {
    return request.get('/categories')
}

// 根据ID获取分类详情
export const getCategoryById = (category_id) => {
    return request.get(`/categories/${category_id}`)
}