import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Plus, Trash2, Pencil, Eye, Copy } from 'lucide-react'
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
import { getClients, createClient, updateClient, deleteClient, getClientCredentials } from '@/api/clients'
import type { Client, ClientCredentials } from '@/types'

export function Clients() {
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [credDialogOpen, setCredDialogOpen] = useState(false)
  const [editClient, setEditClient] = useState<Client | null>(null)
  const [credentials, setCredentials] = useState<ClientCredentials | null>(null)
  const [name, setName] = useState('')

  const load = async () => {
    try {
      const data = await getClients()
      setClients(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditClient(null)
    setName('')
    setDialogOpen(true)
  }

  const openEdit = (client: Client) => {
    setEditClient(client)
    setName(client.name)
    setDialogOpen(true)
  }

  const openCredentials = async (client: Client) => {
    try {
      const creds = await getClientCredentials(client.id)
      setCredentials(creds)
      setCredDialogOpen(true)
    } catch {
      toast.error('Failed to load credentials')
    }
  }

  const handleSave = async () => {
    try {
      if (editClient) {
        await updateClient(editClient.id, { name })
        toast.success('Client updated')
      } else {
        await createClient({ name })
        toast.success('Client created')
      }
      setDialogOpen(false)
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteClient(id)
      toast.success('Client deleted')
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const handleToggle = async (client: Client) => {
    try {
      await updateClient(client.id, { is_active: !client.is_active })
      load()
    } catch {
      toast.error('Something went wrong')
    }
  }

  const copyToClipboard = (value: string, label: string) => {
    navigator.clipboard.writeText(value)
    toast.success(`${label} copied!`)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Clients</h1>
        <Button onClick={openCreate}>
          <Plus className="w-4 h-4 mr-2" />
          Add Client
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : clients.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  No clients yet
                </TableCell>
              </TableRow>
            ) : (
              clients.map((client) => (
                <TableRow key={client.id}>
                  <TableCell className="font-medium">{client.name}</TableCell>
                  <TableCell>
                    <Badge
                      variant={client.is_active ? 'default' : 'secondary'}
                      className="cursor-pointer"
                      onClick={() => handleToggle(client)}
                    >
                      {client.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(client.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => openCredentials(client)}>
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => openEdit(client)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(client.id)}>
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Edit/Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editClient ? 'Edit Client' : 'Add Client'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Client name"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Credentials Dialog */}
      <Dialog open={credDialogOpen} onOpenChange={setCredDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Client Credentials</DialogTitle>
          </DialogHeader>
          {credentials && (
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label>VLESS UUID (Xray)</Label>
                <div className="flex items-center gap-2">
                  <Input value={credentials.xray_uuid} readOnly className="font-mono text-xs" />
                  <Button variant="ghost" size="icon" onClick={() => copyToClipboard(credentials.xray_uuid, 'UUID')}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Hysteria2 Password</Label>
                <div className="flex items-center gap-2">
                  <Input value={credentials.hysteria2_password} readOnly className="font-mono text-xs" />
                  <Button variant="ghost" size="icon" onClick={() => copyToClipboard(credentials.hysteria2_password, 'Password')}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              {credentials.naiveproxy_username && (
                <div className="space-y-2">
                  <Label>NaiveProxy Username</Label>
                  <div className="flex items-center gap-2">
                    <Input value={credentials.naiveproxy_username} readOnly className="font-mono text-xs" />
                    <Button variant="ghost" size="icon" onClick={() => copyToClipboard(credentials.naiveproxy_username!, 'Username')}>
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
              {credentials.naiveproxy_password && (
                <div className="space-y-2">
                  <Label>NaiveProxy Password</Label>
                  <div className="flex items-center gap-2">
                    <Input value={credentials.naiveproxy_password} readOnly className="font-mono text-xs" />
                    <Button variant="ghost" size="icon" onClick={() => copyToClipboard(credentials.naiveproxy_password!, 'Password')}>
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setCredDialogOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
