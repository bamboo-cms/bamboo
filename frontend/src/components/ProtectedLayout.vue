<script setup lang="ts">
import User from '@/components/User.vue'
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
