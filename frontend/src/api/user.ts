import { client } from './fetcher'
import type { IAuthResponse, ICurrentUser } from '@/schema'

export function login(username: string, password: string) {
  return client.post<IAuthResponse>('auth/login', { username, password })
}

export function fetchCurrentUser() {
  return client.get<ICurrentUser>('auth/current')
}
