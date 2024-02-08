<script setup lang="ts">
import { useCurrentUser } from '@/lib/states'

const { currentUser } = useCurrentUser()
</script>

<template>
  <div>{{ currentUser?.name }}</div>
</template>
