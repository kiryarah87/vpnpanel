import api from './client'
import type { Client } from '@/types'

export const getClients = async (): Promise<Client[]> => {
  const response = await api.get<Client[]>('/api/v1/clients')
  return response.data
}

export const createClient = async (data: Partial<Client>): Promise<Client> => {
  const response = await api.post<Client>('/api/v1/clients', data)
  return response.data
}

export const updateClient = async (id: number, data: Partial<Client>): Promise<Client> => {
  const response = await api.patch<Client>(`/api/v1/clients/${id}`, data)
  return response.data
}

export const deleteClient = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/clients/${id}`)
}

export const getClientCredentials = async (clientId: number) => {
  const response = await api.get(`/api/v1/clients/${clientId}/credentials`)
  return response.data
}
