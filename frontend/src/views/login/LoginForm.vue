<script setup lang="ts">
import { ref } from 'vue'

import { useRoute, useRouter } from 'vue-router'
import { useSnackbar } from 'vue3-snackbar'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from '@/components/ui/form'
import LucideSpinner from '~icons/lucide/loader-2'
import { login } from '@/api/user'
import { useGlobalState } from '@/lib/states'

const form = ref({
  username: '',
  password: '',
})
const state = useGlobalState()
const router = useRouter()
const route = useRoute()
const snackbar = useSnackbar()

const isLoading = ref(false)
async function onSubmit(event: Event) {
  event.preventDefault()
  isLoading.value = true
  const { username, password } = form.value

  login(username, password).then((resp) => {
    state.value.accessToken = resp.data.access_token
    state.value.refreshToken = resp.data.refresh_token
    const nextPath = route.query.next ?? '/'
    router.push({ path: nextPath as string })
    snackbar.add({
      text: `Welcome back, ${username}!`,
      type: 'success',
    })
  }).catch((e) => {
    snackbar.add({
      text: e.response.data.message,
      type: 'error',
    })
  }).finally(() => {
    isLoading.value = false
  })
}
</script>

<template>
  <form :class="cn('flex', 'flex-col', 'gap-3', $attrs.class ?? '')" @submit="onSubmit">
    <h1 class="text-2xl font-semibold text-center mb-6">
      Welcome to Bamboo
    </h1>
    <FormField name="username">
      <FormItem>
        <FormLabel>Username</FormLabel>
        <FormControl>
          <Input
            v-model="form.username"
            placeholder="Username"
            auto-capitalize="none"
            auto-correct="off"
            :disabled="isLoading"
          />
        </FormControl>
      </FormItem>
    </FormField>
    <FormField name="password">
      <FormItem>
        <FormLabel>Password</FormLabel>
        <FormControl>
          <Input
            v-model="form.password"
            placeholder="Password"
            type="password"
            auto-capitalize="none"
            :disabled="isLoading"
          />
        </FormControl>
      </FormItem>
    </FormField>
    <Button :disabled="isLoading" type="submit">
      <LucideSpinner v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
      Login
    </Button>
    <div class="border-t-2 border-neutral-200" />
    <div class="flex justify-center gap-3 text-slate-500 dark:text-slate-300">
      <a href="https://github.com/bamboo-cms/bamboo" target="_blank">GitHub</a>
      <a href="https://github.com/bamboo-cms/bamboo" target="_blank">Docs</a>
    </div>
  </form>
</template>
