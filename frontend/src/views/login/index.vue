<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from './LoginForm.vue'
import { useCurrentUser } from '@/lib/states'

const { currentUser } = useCurrentUser()
const router = useRouter()

onMounted(() => {
  if (currentUser.value)
    router.push('/')
})
</script>

<template>
  <div class="flex items-stretch h-screen">
    <div class="bg-slate-800 text-white flex-1" />
    <div class="flex-1 dark:bg-neutral-800 dark:text-white flex justify-center items-center">
      <div class="w-64">
        <LoginForm />
      </div>
    </div>
  </div>
</template>
