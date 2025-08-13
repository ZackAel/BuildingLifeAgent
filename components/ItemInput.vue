<template>
  <form @submit.prevent="submit">
    <input
      v-model="text"
      @keyup.enter="submit"
      placeholder="Add item"
    />
    <button type="submit">Add</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const emit = defineEmits<{ (e: 'submit', value: string): void }>();
const text = ref('');

function submit() {
  const value = text.value.trim();
  if (!value) return;
  emit('submit', value);
  text.value = '';
}
</script>

<style scoped>
form {
  display: flex;
  gap: 0.5rem;
}
input {
  flex: 1;
}
</style>
