<script setup lang="ts">
import { Vue3Snackbar } from 'vue3-snackbar'
</script>

<template>
  <RouterView />
  <Vue3Snackbar top :duration="4000" />
</template>
