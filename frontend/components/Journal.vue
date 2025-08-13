<template>
  <div class="journal">
    <h2>Journal</h2>
    <textarea v-model="newEntry" placeholder="Write a new entry..."></textarea>
    <button @click="addEntry" :disabled="!newEntry.trim()">Save Entry</button>

    <div class="entries" v-if="entries.length">
      <h3>Previous Entries</h3>
      <ul>
        <li v-for="entry in entries" :key="entry.timestamp">
          <div class="timestamp">{{ formatDate(entry.timestamp) }}</div>
          <div class="text">{{ entry.text }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import type { JournalEntry } from '../services/journalService';
import { saveEntry, getEntries } from '../services/journalService';

export default defineComponent({
  name: 'Journal',
  setup() {
    const newEntry = ref('');
    const entries = ref<JournalEntry[]>([]);

    const loadEntries = async () => {
      entries.value = await getEntries();
    };

    const addEntry = async () => {
      if (!newEntry.value.trim()) return;
      await saveEntry(newEntry.value);
      newEntry.value = '';
      await loadEntries();
    };

    const formatDate = (ts: number) => new Date(ts).toLocaleString();

    onMounted(loadEntries);

    return { newEntry, entries, addEntry, formatDate };
  }
});
</script>

<style scoped>
.journal {
  display: flex;
  flex-direction: column;
  max-width: 600px;
}

textarea {
  width: 100%;
  min-height: 80px;
  margin-bottom: 0.5rem;
}

button {
  align-self: flex-end;
}

.entries {
  margin-top: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.entries ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.entries li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ccc;
}

.timestamp {
  font-size: 0.8rem;
  color: #667;
}
</style>

