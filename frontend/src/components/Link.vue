<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  to: string
  class?: string
  underline?: boolean
}>(), { underline: true })

const isOuterLink = computed(() => props.to.startsWith('http') || props.to.startsWith('mailto'))

const classes = computed(() => cn(
  props.underline && 'underline',
  props.class,
))
</script>

<template>
  <a
    v-if="isOuterLink"
    :href="props.to"
    :class="classes"
    v-bind="$attrs"
  >
    <slot />
  </a>
  <RouterLink
    v-else
    :to="props.to"
    :class="classes"
    v-bind="$attrs"
  >
    <slot />
  </RouterLink>
</template>
