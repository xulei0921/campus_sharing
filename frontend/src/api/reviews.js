import request from '@/utils/request'

// 创建评价
export const createReview = (reviewData) => {
    return request.post('/reviews/', reviewData)
}

// 获取指定用户收到的评价
export const getUserReviews = (user_id) => {
    return request.get(`/reviews/user/${user_id}`)
}

// 获取指定交易的评价
export const getTransactionReview = (transaction_id) => {
    return request.get(`/reviews/transaction/${transaction_id}`)
}