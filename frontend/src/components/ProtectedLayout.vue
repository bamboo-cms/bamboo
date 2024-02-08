<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSnackbar } from 'vue3-snackbar'
import { fetchCurrentUser } from '@/api/user'
import User from '@/components/User.vue'
import { useCurrentUser } from '@/lib/states'

const { setCurrentUser } = useCurrentUser()
const router = useRouter()
const route = useRoute()
const snackbar = useSnackbar()

onMounted(async () => {
  try {
    const resp = await fetchCurrentUser()
    setCurrentUser(resp.data)
  }
  catch (e) {
    setCurrentUser(undefined)
    router.push({ path: '/login', query: { next: route.path } })
    snackbar.add({
      text: 'You need to login to access this page',
      type: 'error',
    })
  }
})
</script>

<template>
  <div class="flex h-screen items-stretch">
    <div class="w-[320px] text-white bg-slate-800">
      Sidebar
      <User />
    </div>
    <div class="flex-1">
      <RouterView />
    </div>
  </div>
</template>
