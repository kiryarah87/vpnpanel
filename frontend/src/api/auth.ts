import api from './client'
import type { Token } from '@/types'

export const login = async (username: string, password: string): Promise<Token> => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  const response = await api.post<Token>('/api/v1/auth/login', formData)
  return response.data
}

export const getMe = async () => {
  const response = await api.get('/api/v1/auth/me')
  return response.data
}
