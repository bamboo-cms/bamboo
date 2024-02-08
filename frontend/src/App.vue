<script setup lang="ts">
import { Vue3Snackbar } from 'vue3-snackbar'
import { useDark } from '@vueuse/core'
import { cn } from './lib/utils'

const isDark = useDark()
</script>

<template>
  <div :class="cn('bg-background', 'text-foreground', isDark && 'dark')">
    <RouterView />
  </div>
  <Vue3Snackbar top :duration="4000" />
</template>
