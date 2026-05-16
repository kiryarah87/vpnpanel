import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Plus, Trash2, Pencil } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getInbounds, createInbound, updateInbound, deleteInbound } from '@/api/inbounds'
import { getDomains } from '@/api/domains'
import type { Inbound, Domain } from '@/types'

const PROTOCOLS = ['vless-tcp-reality', 'vless-xhttp-reality', 'hysteria2', 'naiveproxy']
const REALITY_PROTOCOLS = ['vless-tcp-reality', 'vless-xhttp-reality']

export function Inbounds() {
  const [inbounds, setInbounds] = useState<Inbound[]>([])
  const [domains, setDomains] = useState<Domain[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editInbound, setEditInbound] = useState<Inbound | null>(null)
  const [form, setForm] = useState({
    protocol: PROTOCOLS[0], port: '', tag: '', sni: '', domain_id: ''
  })

  const load = async () => {
    try {
      const [inboundsData, domainsData] = await Promise.all([getInbounds(), getDomains()])
      setInbounds(inboundsData)
      setDomains(domainsData)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditInbound(null)
    setForm({ protocol: PROTOCOLS[0], port: '', tag: '', sni: '', domain_id: '' })
    setDialogOpen(true)
  }

  const openEdit = (inbound: Inbound) => {
    setEditInbound(inbound)
    setForm({
      protocol: inbound.protocol,
      port: String(inbound.port ?? ''),
      tag: inbound.tag ?? '',
      sni: inbound.sni ?? '',
      domain_id: String(inbound.domain_id ?? ''),
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    try {
      const portValue = form.port ? Number(form.port) : undefined
      const portType = form.port ? 'fixed' : 'random'
      const domainId = form.domain_id ? Number(form.domain_id) : undefined

      if (editInbound) {
        await updateInbound(editInbound.id, { ...form, port: portValue, port_type: portType, domain_id: domainId })
        toast.success('Inbound updated')
      } else {
        await createInbound({ ...form, port: portValue, port_type: portType, domain_id: domainId })
        toast.success('Inbound created')
      }
      setDialogOpen(false)
      load()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Something went wrong')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteInbound(id)
      toast.success('Inbound deleted')
      load()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Something went wrong')
    }
  }

  const handleToggle = async (inbound: Inbound) => {
    try {
      await updateInbound(inbound.id, { is_active: !inbound.is_active })
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Inbounds</h1>
        <Button onClick={openCreate}>
          <Plus className="w-4 h-4 mr-2" />
          Add Inbound
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tag</TableHead>
              <TableHead>Protocol</TableHead>
              <TableHead>Port</TableHead>
              <TableHead>SNI / Domain</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">Loading...</TableCell>
              </TableRow>
            ) : inbounds.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">No inbounds yet</TableCell>
              </TableRow>
            ) : (
              inbounds.map((inbound) => (
                <TableRow key={inbound.id}>
                  <TableCell className="font-medium">{inbound.tag}</TableCell>
                  <TableCell><Badge variant="outline">{inbound.protocol}</Badge></TableCell>
                  <TableCell>{inbound.port}</TableCell>
                  <TableCell>
                    {REALITY_PROTOCOLS.includes(inbound.protocol)
                      ? (inbound.domain_id
                          ? domains.find(d => d.id === inbound.domain_id)?.name ?? inbound.sni ?? '-'
                          : inbound.sni ?? '-')
                      : 'server domain'}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={inbound.is_active ? 'default' : 'secondary'}
                      className="cursor-pointer"
                      onClick={() => handleToggle(inbound)}
                    >
                      {inbound.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(inbound)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(inbound.id)}>
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editInbound ? 'Edit Inbound' : 'Add Inbound'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Protocol</Label>
              <select
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                value={form.protocol}
                onChange={(e) => setForm({ ...form, protocol: e.target.value, sni: '', domain_id: '' })}
              >
                {PROTOCOLS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <Label>Port <span className="text-muted-foreground text-xs">(оставьте пустым для случайного)</span></Label>
              <Input
                type="number"
                value={form.port}
                onChange={(e) => setForm({ ...form, port: e.target.value })}
                placeholder="random"
              />
            </div>

            <div className="space-y-2">
              <Label>Tag</Label>
              <Input
                value={form.tag}
                onChange={(e) => setForm({ ...form, tag: e.target.value })}
                placeholder="vless-reality"
              />
            </div>

            {/* Reality — выбор домена из списка для SNI маскировки */}
            {REALITY_PROTOCOLS.includes(form.protocol) && (
              <div className="space-y-2">
                <Label>SNI (маскировочный домен)</Label>
                {domains.filter(d => d.is_active).length > 0 ? (
                  <select
                    className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                    value={form.domain_id}
                    onChange={(e) => {
                      const domain = domains.find(d => d.id === Number(e.target.value))
                      setForm({ ...form, domain_id: e.target.value, sni: domain?.name ?? '' })
                    }}
                  >
                    <option value="">— Ввести вручную —</option>
                    {domains.filter(d => d.is_active).map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                ) : null}
                {!form.domain_id && (
                  <Input
                    value={form.sni}
                    onChange={(e) => setForm({ ...form, sni: e.target.value })}
                    placeholder="example.com"
                  />
                )}
              </div>
            )}

            {/* Hysteria2 / NaiveProxy — используют системный домен */}
            {!REALITY_PROTOCOLS.includes(form.protocol) && (
              <div className="space-y-2">
                <Label>Domain</Label>
                <p className="text-sm text-muted-foreground px-1">
                  Используется системный домен сервера из конфигурации
                </p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
