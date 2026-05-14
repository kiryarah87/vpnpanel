import { useEffect, useState } from 'react'
import { Users, Network, Globe, Activity } from 'lucide-react'
import { getClients } from '@/api/clients'
import { getInbounds } from '@/api/inbounds'

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

  useEffect(() => {
    getClients().then((data) => {
      setClientsCount(data.length)
      setActiveClients(data.filter((c) => c.is_active).length)
    })
    getInbounds().then((data) => {
      setInboundsCount(data.length)
      setActiveInbounds(data.filter((i) => i.is_active).length)
    })
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Clients" value={clientsCount} icon={<Users className="w-5 h-5" />} />
        <StatCard title="Active Clients" value={activeClients} icon={<Activity className="w-5 h-5" />} />
        <StatCard title="Total Inbounds" value={inboundsCount} icon={<Network className="w-5 h-5" />} />
        <StatCard title="Active Inbounds" value={activeInbounds} icon={<Globe className="w-5 h-5" />} />
      </div>
    </div>
  )
}
