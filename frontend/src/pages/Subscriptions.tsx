import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Plus, Trash2, Pencil, Copy, ExternalLink } from 'lucide-react'
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
import {
  getSubscriptions,
  createSubscription,
  updateSubscription,
  deleteSubscription,
} from '@/api/subscriptions'
import { getClients } from '@/api/clients'
import { getInbounds } from '@/api/inbounds'
import type { Subscription, Client, Inbound } from '@/types'

export function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [inbounds, setInbounds] = useState<Inbound[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editSub, setEditSub] = useState<Subscription | null>(null)
  const [form, setForm] = useState({
    name: '',
    client_id: 0,
    inbound_ids: [] as number[],
  })

  const load = async () => {
    try {
      const [subs, cls, inbs] = await Promise.all([
        getSubscriptions(),
        getClients(),
        getInbounds(),
      ])
      setSubscriptions(subs)
      setClients(cls)
      setInbounds(inbs)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditSub(null)
    setForm({ name: '', client_id: clients[0]?.id ?? 0, inbound_ids: [] })
    setDialogOpen(true)
  }

  const openEdit = (sub: Subscription) => {
    setEditSub(sub)
    setForm({
      name: sub.name,
      client_id: sub.client_id,
      inbound_ids: sub.inbounds.map((i) => i.id),
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    try {
      if (editSub) {
        await updateSubscription(editSub.id, {
          name: form.name,
          inbound_ids: form.inbound_ids,
        })
        toast.success('Subscription updated')
      } else {
        await createSubscription(form)
        toast.success('Subscription created')
      }
      setDialogOpen(false)
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteSubscription(id)
      toast.success('Subscription deleted')
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const handleToggle = async (sub: Subscription) => {
    try {
      await updateSubscription(sub.id, { is_active: !sub.is_active })
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const getSubUrl = (token: string) =>
    `${import.meta.env.VITE_API_URL}/sub/${token}`

  const copyUrl = (token: string) => {
    navigator.clipboard.writeText(getSubUrl(token))
    toast.success('URL copied!')
  }

  const toggleInbound = (id: number) => {
    setForm((prev) => ({
      ...prev,
      inbound_ids: prev.inbound_ids.includes(id)
        ? prev.inbound_ids.filter((i) => i !== id)
        : [...prev.inbound_ids, id],
    }))
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Subscriptions</h1>
        <Button onClick={openCreate}>
          <Plus className="w-4 h-4 mr-2" />
          Add Subscription
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Client</TableHead>
              <TableHead>Inbounds</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>URL</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : subscriptions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  No subscriptions yet
                </TableCell>
              </TableRow>
            ) : (
              subscriptions.map((sub) => (
                <TableRow key={sub.id}>
                  <TableCell className="font-medium">{sub.name}</TableCell>
                  <TableCell>
                    {clients.find((c) => c.id === sub.client_id)?.name ?? sub.client_id}
                  </TableCell>
                  <TableCell>{sub.inbounds?.length ?? 0}</TableCell>
                  <TableCell>
                    <Badge
                      variant={sub.is_active ? 'default' : 'secondary'}
                      className="cursor-pointer"
                      onClick={() => handleToggle(sub)}
                    >
                      {sub.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon" onClick={() => copyUrl(sub.token)}>
                        <Copy className="w-4 h-4" />
                      </Button>
                      <a href={getSubUrl(sub.token)} target="_blank" rel="noreferrer">
                        <Button variant="ghost" size="icon">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </a>
                    </div>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(sub)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(sub.id)}>
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
            <DialogTitle>{editSub ? 'Edit Subscription' : 'Add Subscription'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="My Subscription"
              />
            </div>
            {!editSub && (
              <div className="space-y-2">
                <Label>Client</Label>
                <select
                  className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                  value={form.client_id}
                  onChange={(e) => setForm({ ...form, client_id: Number(e.target.value) })}
                >
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="space-y-2">
              <Label>Inbounds</Label>
              <div className="space-y-2 max-h-40 overflow-y-auto border rounded-md p-2">
                {inbounds.map((inbound) => (
                  <label key={inbound.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.inbound_ids.includes(inbound.id)}
                      onChange={() => toggleInbound(inbound.id)}
                    />
                    <span className="text-sm">{inbound.tag} — {inbound.protocol}:{inbound.port}</span>
                  </label>
                ))}
              </div>
            </div>
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
