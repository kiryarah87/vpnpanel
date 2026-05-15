import { ThemeProvider } from '@/components/theme-provider'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Layout } from '@/components/layout'
import { Login, Dashboard, Inbounds, Clients, Domains, Settings, Subscriptions } from '@/pages'
import { useAuthStore } from '@/store'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <ThemeProvider>
        <TooltipProvider>
            <BrowserRouter>
                <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                    path="/"
                    element={
                    <PrivateRoute>
                        <Layout />
                    </PrivateRoute>
                    }
                >
                    <Route index element={<Dashboard />} />
                    <Route path="inbounds" element={<Inbounds />} />
                    <Route path="clients" element={<Clients />} />
                    <Route path="subscriptions" element={<Subscriptions />} />
                    <Route path="domains" element={<Domains />} />
                    <Route path="settings" element={<Settings />} />
                </Route>
                </Routes>
            </BrowserRouter>
        </TooltipProvider>
    </ThemeProvider>
  )
}

export default App
