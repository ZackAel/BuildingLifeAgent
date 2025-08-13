<template>
  <div class="tasks">
    <input
      v-model="newTask"
      @keyup.enter="addTask"
      placeholder="Add a task"
    />
    <button @click="addTask">Add</button>
    <ul>
      <li v-for="task in tasks" :key="task.id">
        <input type="checkbox" v-model="task.done" @change="toggleDone(task)" />
        <span v-if="!task.editing" :class="{ done: task.done }">{{ task.text }}</span>
        <input
          v-else
          v-model="task.text"
          @keyup.enter="finishEdit(task)"
          @blur="finishEdit(task)"
        />
        <button v-if="!task.editing" @click="startEdit(task)">Edit</button>
        <button v-if="task.editing" @click="finishEdit(task)">Save</button>
        <button @click="deleteTask(task)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import tasksService, { Task } from './tasksService';

interface UiTask extends Task {
  editing?: boolean;
}

export default defineComponent({
  name: 'Tasks',
  setup() {
    const newTask = ref('');
    const tasks = ref<UiTask[]>([]);

    onMounted(() => {
      tasks.value = tasksService.getTasks();
    });

    const addTask = () => {
      const text = newTask.value.trim();
      if (!text) return;
      tasksService.addTask(text);
      tasks.value = tasksService.getTasks();
      newTask.value = '';
    };

    const startEdit = (task: UiTask) => {
      task.editing = true;
    };

    const finishEdit = (task: UiTask) => {
      if (!task.text.trim()) {
        deleteTask(task);
        return;
      }
      task.editing = false;
      tasksService.updateTask(task);
    };

    const toggleDone = (task: UiTask) => {
      tasksService.updateTask(task);
    };

    const deleteTask = (task: UiTask) => {
      tasksService.deleteTask(task.id);
      tasks.value = tasksService.getTasks();
    };

    return {
      newTask,
      tasks,
      addTask,
      startEdit,
      finishEdit,
      toggleDone,
      deleteTask,
    };
  },
});
</script>

<style scoped>
.tasks {
  max-width: 400px;
}
.done {
  text-decoration: line-through;
}
</style>
