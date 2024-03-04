<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import LoginForm from './LoginForm.vue'
import { useCurrentUser } from '@/lib/states'
import { Button } from '@/components/ui/button'
import LucideSun from '~icons/lucide/sun'
import LucideMoon from '~icons/lucide/moon'
import LogoDark from '@/assets/logo-dark.svg?component'
import Link from '@/components/Link.vue'

const { currentUser } = useCurrentUser()
const router = useRouter()

const isDark = useDark()
const toggleDark = useToggle(isDark)

onMounted(() => {
  if (currentUser.value)
    router.push('/')
})
</script>

<template>
  <div class="flex items-stretch h-screen">
    <div class="bg-slate-800 text-white flex-1 flex flex-col p-3">
      <Link to="/" :underline="false">
        <LogoDark width="120" />
      </Link>
      <div class="flex flex-1 items-center justify-center">
        <div class="font-bold text-6xl max-w-[480px] bg-gradient-to-r from-indigo-500 to-teal-400 bg-clip-text text-transparent">
          A CMS optimized for conference hosting
        </div>
      </div>
      <div class="text-center">
        Copyright © 2024, <Link to="https://github.com/bamboo-cms" target="_blank">
          Bamboo Team
        </Link>.
      </div>
    </div>
    <div class="flex-1 flex justify-center items-center relative">
      <Button size="icon" variant="ghost" class="absolute top-1 right-1" @click="toggleDark()">
        <LucideSun v-if="isDark" />
        <LucideMoon v-else />
      </Button>
      <div class="w-64">
        <LoginForm />
      </div>
    </div>
  </div>
</template>
