import api from './client'
import type { Subscription } from '@/types'

export const getSubscriptions = async (): Promise<Subscription[]> => {
  const response = await api.get<Subscription[]>('/api/v1/subscriptions/')
  return response.data
}

export const getSubscription = async (id: number): Promise<Subscription> => {
  const response = await api.get<Subscription>(`/api/v1/subscriptions/${id}`)
  return response.data
}

export const createSubscription = async (data: {
  name: string
  client_id: number
  inbound_ids: number[]
}): Promise<Subscription> => {
  const response = await api.post<Subscription>('/api/v1/subscriptions/', data)
  return response.data
}

export const updateSubscription = async (
  id: number,
  data: { name?: string; is_active?: boolean; inbound_ids?: number[] }
): Promise<Subscription> => {
  const response = await api.patch<Subscription>(`/api/v1/subscriptions/${id}`, data)
  return response.data
}

export const deleteSubscription = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/subscriptions/${id}`)
}
