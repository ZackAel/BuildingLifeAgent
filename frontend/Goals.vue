<template>
    <div class="goals">
      <h2>Goals</h2>
      <form @submit.prevent="addGoal">
        <input v-model="newGoal.title" placeholder="Goal title" required />
        <input type="date" v-model="newGoal.startDate" required />
        <input type="date" v-model="newGoal.targetDate" required />
        <button type="submit">Add Goal</button>
      </form>
      <ul>
        <li v-for="goal in goals" :key="goal.id">
          <input type="checkbox" v-model="goal.completed" @change="saveGoals" />
          <span :class="{completed: goal.completed}">{{ goal.title }}</span>
          <progress :value="getProgress(goal)" max="100"></progress>
          <span>{{ getProgress(goal).toFixed(0) }}%</span>
        </li>
      </ul>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, reactive, onMounted } from 'vue';
  import goalsService, { Goal } from './goalsService';
  
  export default defineComponent({
    name: 'Goals',
    setup() {
      const goals = reactive<Goal[]>([]);
      const newGoal = reactive<{title: string; startDate: string; targetDate: string}>(
        {
          title: '',
          startDate: '',
          targetDate: ''
        }
      );
  
      const load = () => {
        const loaded = goalsService.loadGoals();
        goals.splice(0, goals.length, ...loaded);
      };
  
      const saveGoals = () => goalsService.saveGoals(goals);
  
      const addGoal = () => {
        goals.push({
          id: Date.now(),
          title: newGoal.title,
          startDate: new Date(newGoal.startDate),
          targetDate: new Date(newGoal.targetDate),
          completed: false
        });
        saveGoals();
        newGoal.title = '';
        newGoal.startDate = '';
        newGoal.targetDate = '';
      };
  
      const getProgress = (goal: Goal) => goalsService.calculateProgress(goal);
  
      onMounted(load);
  
      return { goals, newGoal, addGoal, getProgress, saveGoals };
    }
  });
  </script>
  
  <style scoped>
  .completed {
    text-decoration: line-through;
  }
  </style>
  