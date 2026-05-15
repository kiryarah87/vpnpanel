import { useEffect, useState } from 'react'
import { Users, Network, Globe, Activity, BookOpen } from 'lucide-react'
import { getClients } from '@/api/clients'
import { getInbounds } from '@/api/inbounds'
import { getSubscriptions } from '@/api/subscriptions'
import { Badge } from '@/components/ui/badge'
import type { Client, Inbound } from '@/types'

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
}

function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div className="rounded-lg border bg-card p-6 flex items-center gap-4">
      <div className="p-3 rounded-md bg-muted">{icon}</div>
      <div>
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  )
}

export function Dashboard() {
  const [clientsCount, setClientsCount] = useState(0)
  const [inboundsCount, setInboundsCount] = useState(0)
  const [activeInbounds, setActiveInbounds] = useState(0)
  const [activeClients, setActiveClients] = useState(0)
  const [subsCount, setSubsCount] = useState(0)
  const [recentClients, setRecentClients] = useState<Client[]>([])
  const [recentInbounds, setRecentInbounds] = useState<Inbound[]>([])

  useEffect(() => {
    getClients().then((data) => {
      setClientsCount(data.length)
      setActiveClients(data.filter((c) => c.is_active).length)
      setRecentClients(data.slice(-5).reverse())
    })
    getInbounds().then((data) => {
      setInboundsCount(data.length)
      setActiveInbounds(data.filter((i) => i.is_active).length)
      setRecentInbounds(data.slice(-5).reverse())
    })
    getSubscriptions().then((data) => {
      setSubsCount(data.length)
    })
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard title="Total Clients" value={clientsCount} icon={<Users className="w-5 h-5" />} />
        <StatCard title="Active Clients" value={activeClients} icon={<Activity className="w-5 h-5" />} />
        <StatCard title="Total Inbounds" value={inboundsCount} icon={<Network className="w-5 h-5" />} />
        <StatCard title="Active Inbounds" value={activeInbounds} icon={<Globe className="w-5 h-5" />} />
        <StatCard title="Subscriptions" value={subsCount} icon={<BookOpen className="w-5 h-5" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Clients</h2>
          {recentClients.length === 0 ? (
            <p className="text-muted-foreground text-sm">No clients yet</p>
          ) : (
            <div className="space-y-3">
              {recentClients.map((client) => (
                <div key={client.id} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{client.name}</span>
                  <Badge variant={client.is_active ? 'default' : 'secondary'}>
                    {client.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Inbounds</h2>
          {recentInbounds.length === 0 ? (
            <p className="text-muted-foreground text-sm">No inbounds yet</p>
          ) : (
            <div className="space-y-3">
              {recentInbounds.map((inbound) => (
                <div key={inbound.id} className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium">{inbound.tag}</span>
                    <span className="text-xs text-muted-foreground ml-2">{inbound.protocol}:{inbound.port}</span>
                  </div>
                  <Badge variant={inbound.is_active ? 'default' : 'secondary'}>
                    {inbound.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
