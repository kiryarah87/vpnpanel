import api from './client'
import type { Domain } from '@/types'

export const getDomains = async (): Promise<Domain[]> => {
  const response = await api.get('/api/v1/domains/')
  return response.data
}

export const createDomain = async (data: Partial<Domain>): Promise<Domain> => {
  const response = await api.post('/api/v1/domains/', data)
  return response.data
}

export const updateDomain = async (id: number, data: Partial<Domain>): Promise<Domain> => {
  const response = await api.patch(`/api/v1/domains/${id}`, data)
  return response.data
}

export const deleteDomain = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/domains/${id}`)
}
