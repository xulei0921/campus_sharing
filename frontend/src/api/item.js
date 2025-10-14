import request from '@/utils/request'

// 发布新物品
export const createItem = ({title, description, price, category_id, location, images}) => {
    return request.post('/items/', { title, description, price, category_id, location, images })
}

// 获取物品列表
export const getItems = (params) => {
    // 合并默认参数和传入参数（默认第一页，每页10条）
    const queryParams = {
        page: 1,
        limit: 10,
        ...params
    }

    return request.get('/items/', {
        params: queryParams
    })
}

// 上传物品图片
export const uploadItemImages = (files) => {
    const formData = new FormData()
    files.forEach(file => {
        formData.append('files', file)
    })
    return request.post('/items/upload-image', formData)
} 