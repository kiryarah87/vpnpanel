export interface User {
  id: number
  username: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Inbound {
  id: number
  protocol: string
  port: number
  port_type: string
  tag: string
  sni: string | null
  is_active: boolean
  domain_id?: number
  created_at: string
  updated_at: string
}

export interface Client {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Credential {
  id: number
  client_id: number
  vless_uuid?: string
  hysteria2_password?: string
  naiveproxy_username?: string
  naiveproxy_password?: string
}

export interface Domain {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface Subscription {
  id: number
  name: string
  token: string
  is_active: boolean
  client_id: number
  inbounds: Inbound[]
  created_at: string
  updated_at: string
}
