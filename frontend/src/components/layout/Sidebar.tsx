import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, Network, Globe, Settings, BookOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/inbounds', label: 'Inbounds', icon: Network },
  { to: '/clients', label: 'Clients', icon: Users },
  { to: '/subscriptions', label: 'Subscriptions', icon: BookOpen },
  { to: '/domains', label: 'Domains', icon: Globe },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  return (
    <aside className="w-60 border-r bg-sidebar flex flex-col">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="font-bold text-lg">VPN Panel</span>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
              )
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
