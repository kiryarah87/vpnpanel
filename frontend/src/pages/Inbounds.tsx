import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Plus, Trash2, Pencil } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getInbounds, createInbound, updateInbound, deleteInbound } from '@/api/inbounds'
import type { Inbound } from '@/types'

const PROTOCOLS = ['vless-tcp-reality', 'vless-xhttp-reality', 'hysteria2', 'naiveproxy']
const REALITY_PROTOCOLS = ['vless-tcp-reality', 'vless-xhttp-reality']

export function Inbounds() {
  const [inbounds, setInbounds] = useState<Inbound[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editInbound, setEditInbound] = useState<Inbound | null>(null)
  const [form, setForm] = useState({ protocol: PROTOCOLS[0], port: '', port_type: 'fixed', tag: '', sni: '' })

  const load = async () => {
    try {
      const data = await getInbounds()
      setInbounds(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditInbound(null)
    setForm({ protocol: PROTOCOLS[0], port: '', port_type: 'fixed', tag: '', sni: '' })
    setDialogOpen(true)
  }

  const openEdit = (inbound: Inbound) => {
    setEditInbound(inbound)
    setForm({ protocol: inbound.protocol, port: String(inbound.port), port_type: 'fixed', tag: inbound.tag, sni: inbound.sni ?? '' })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    try {
      const portValue = form.port ? Number(form.port) : undefined
      const portType = form.port ? 'fixed' : 'random'

      if (editInbound) {
        await updateInbound(editInbound.id, { ...form, port: portValue, port_type: portType })
        toast.success('Inbound updated')
      } else {
        await createInbound({ ...form, port: portValue, port_type: portType })
        toast.success('Inbound created')
      }
      setDialogOpen(false)
      load()
    } catch (error: any) {
      const detail = error?.response?.data?.detail
      toast.error(detail || 'Something went wrong')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteInbound(id)
      toast.success('Inbound deleted')
      load()
    } catch (error: any) {
      const detail = error?.response?.data?.detail
      toast.error(detail || 'Something went wrong')
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
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : inbounds.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No inbounds yet
                </TableCell>
              </TableRow>
            ) : (
              inbounds.map((inbound) => (
                <TableRow key={inbound.id}>
                  <TableCell className="font-medium">{inbound.tag}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{inbound.protocol}</Badge>
                  </TableCell>
                  <TableCell>{inbound.port}</TableCell>
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
                onChange={(e) => setForm({ ...form, protocol: e.target.value })}
              >
                {PROTOCOLS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Port</Label>
              <Input
                type="number"
                value={form.port}
                onChange={(e) => setForm({ ...form, port: e.target.value })}
                placeholder="443"
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
            {REALITY_PROTOCOLS.includes(form.protocol) && (
              <div className="space-y-2">
                <Label>SNI</Label>
                <Input
                  value={form.sni}
                  onChange={(e) => setForm({ ...form, sni: e.target.value })}
                  placeholder="example.com"
                />
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
