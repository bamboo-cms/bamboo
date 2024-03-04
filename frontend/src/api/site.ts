import { useFetch } from './fetcher'

interface ISiteOut {
  id: number
  name: string
  config: string
  templace_url: string
  deployment_target: string
  deployment_method: string
  deployment_secret: string
}

export function useAllSites() {
  return useFetch<ISiteOut[]>('/site/all')
}
