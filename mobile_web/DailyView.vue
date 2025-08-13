<template>
    <div class="daily-view">
      <section class="tasks">
        <h2>Today's Tasks</h2>
        <ul>
          <li v-for="task in tasks" :key="task.id">{{ task.title }}</li>
        </ul>
      </section>
      <section class="journal">
        <h2>Journal Highlight</h2>
        <p v-if="journal">{{ journal }}</p>
        <p v-else>No journal entries for today.</p>
      </section>
      <section class="goals">
        <h2>Goal Progress</h2>
        <ul>
          <li v-for="goal in goals" :key="goal.id">
            {{ goal.title }} - {{ goal.progress }}%
          </li>
        </ul>
      </section>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DailyView',
    props: {
      tasks: { type: Array, default: () => [] },
      journal: { type: String, default: '' },
      goals: { type: Array, default: () => [] }
    }
  };
  </script>
  
  <style scoped>
  .daily-view section {
    margin-bottom: 1em;
  }
  </style>
  