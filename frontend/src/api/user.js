import request from '@/utils/request'

// 注册新用户
export const registerUser = ({ username, email, phone, password }) => {
    return request.post('/users/register', { username, email, phone, password })
}

// 用户登录
export const loginUser = ({ username, password }) => {
    const formData = `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    return request.post('/users/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 获取当前登录用户的信息
export const getCurrentUser = () => {
    return request.get('/users/me')
}

// 更新当前登录用户的信息
export const updateCurrentUser = (data) => {
    return request.put('/users/me', data)
}

// 根据ID获取用户信息
export const getUserById = (userId) => {
    return request.get(`/users/${userId}`)
}