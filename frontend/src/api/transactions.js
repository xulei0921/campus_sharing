import request from '@/utils/request'

// 发起交易请求
export const createTransaction = ({ meeting_time, meeting_location, item_id }) => {
    return request.post('/transactions/', {
        meeting_time,
        meeting_location,
        item_id
    })
}

// 获取当前用户作为买家的交易
export const getCurrentUserBuyTransactions = () => {
    return request.get('/transactions/my-buy')
}

// 获取当前用户作为卖家的交易
export const getCurrentUserSellTransactions = () => {
    return request.get('/transactions/my-sell')
}

// 更新交易信息
export const updateTransaction = (transaction_id, newData) => {
    return request.put(`/transactions/${transaction_id}`, newData)
}