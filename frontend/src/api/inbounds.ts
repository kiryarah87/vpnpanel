import api from './client'
import type { Inbound } from '@/types'

export const getInbounds = async (): Promise<Inbound[]> => {
  const response = await api.get<Inbound[]>('/api/v1/inbounds')
  return response.data
}

export const createInbound = async (data: Partial<Inbound>): Promise<Inbound> => {
  const response = await api.post<Inbound>('/api/v1/inbounds', data)
  return response.data
}

export const updateInbound = async (id: number, data: Partial<Inbound>): Promise<Inbound> => {
  const response = await api.patch<Inbound>(`/api/v1/inbounds/${id}`, data)
  return response.data
}

export const deleteInbound = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/inbounds/${id}`)
}
