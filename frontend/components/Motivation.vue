<template>
  <div class="motivation">
    <p v-if="message">{{ message }}</p>
    <p v-else>Loading motivation...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { startMotivationRefresh } from '../services/motivationService';

const message = ref('');
let stop: (() => void) | null = null;

onMounted(() => {
  stop = startMotivationRefresh((msg: string) => {
    message.value = msg;
  });
});

onUnmounted(() => {
  if (stop) {
    stop();
  }
});
</script>

<style scoped>
.motivation {
  padding: 1rem;
  font-style: italic;
}
</style>

