<template>
  <div class="popup-layout">
    <slot />
  </div>
</template>

<script>
export default {
  name: "PopupLayout"
};
</script>

<style scoped>
@import "../styles/theme.css";

.popup-layout {
  padding: 24px;
  margin: 16px;
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-sm);
  background: var(--color-background);
}
</style>
