<template>
  <div class="clock">{{ time }}</div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const time = ref(new Date().toLocaleTimeString());
let timer: number;

onMounted(() => {
  timer = window.setInterval(() => {
    time.value = new Date().toLocaleTimeString();
  }, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<style scoped>
.clock {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-weight: bold;
}
</style>
