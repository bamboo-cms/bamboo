export interface IAuthResponse {
  access_token: string
  refresh_token: string
}

export interface ICurrentUser {
  name: string
  email: string
  username: string
  profile: string
  is_superuser: boolean
  role: string | null
}
