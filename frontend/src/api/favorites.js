import request from '@/utils/request'

// 收藏物品
export const createFavorite = (id) => {
    return request.post('/favorites/', {item_id: id})
}

// 检查物品是否被当前用户收藏
export const checkItemFavorited = (item_id) => {
    return request.get(`/favorites/item/${item_id}/check`)
}

// 取消收藏物品
export const deleteFavorite = (item_id) => {
    return request.delete(`/favorites/item/${item_id}`)
}

// 获取当前用户的收藏列表
export const readUserFavorites = () => {
    return request.get('/favorites/')
}