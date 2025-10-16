import request from '@/utils/request'

// 发起交易请求
export const createTransaction = ({ meeting_time, meeting_location, item_id }) => {
    return request.post('/transactions/', {
        meeting_time,
        meeting_location,
        item_id
    })
}