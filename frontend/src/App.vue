<script setup lang="ts">
import { Vue3Snackbar } from 'vue3-snackbar'
import { useAllSites } from './api/site'
import { Button } from '@/components/ui/button'

function handleClick() {
  console.log('clicked')
}

useAllSites()
</script>

<template>
  <div class="flex justify-center items-center h-screen flex-col gap-3">
    <h1 class="font-bold text-3xl">
      Hello world
    </h1>
    <Button @click="handleClick">
      Click me
    </Button>
  </div>
  <Vue3Snackbar top :duration="4000" />
</template>
