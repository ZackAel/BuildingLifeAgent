import { loadModule } from 'https://unpkg.com/vue3-sfc-loader/dist/vue3-sfc-loader.esm.js';

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js');
}

const { createApp, defineAsyncComponent } = Vue;

const options = {
  moduleCache: {
    vue: Vue,
  },
  async getFile(url) {
    const res = await fetch(url);
    if (!res.ok) throw Object.assign(new Error(res.statusText), { res });
    return await res.text();
  },
  addStyle(textContent) {
    const style = Object.assign(document.createElement('style'), { textContent });
    const ref = document.head.getElementsByTagName('style')[0] || null;
    document.head.insertBefore(style, ref);
  },
};

const DailyView = defineAsyncComponent(() => loadModule('./DailyView.vue', options));

const Tasks = {
  props: ['tasks'],
  template: `
    <div>
      <h2>Tasks</h2>
      <ul><li v-for="task in tasks" :key="task.id">{{ task.title }}</li></ul>
    </div>
  `,
};

const Journal = {
  props: ['journal'],
  template: `
    <div>
      <h2>Journal</h2>
      <p>{{ journal }}</p>
    </div>
  `,
};

const Goals = {
  props: ['goals'],
  template: `
    <div>
      <h2>Goals</h2>
      <ul><li v-for="goal in goals" :key="goal.id">{{ goal.title }} - {{ goal.progress }}%</li></ul>
    </div>
  `,
};

const app = createApp({
  components: { DailyView, Tasks, Journal, Goals },
  data() {
    return {
      currentTab: 'daily',
      tasks: [{ id: 1, title: 'Sample Task' }],
      journal: 'No journal entries yet.',
      goals: [{ id: 1, title: 'Build Habit', progress: 20 }],
    };
  },
  computed: {
    currentView() {
      return {
        daily: 'DailyView',
        tasks: 'Tasks',
        journal: 'Journal',
        goals: 'Goals',
      }[this.currentTab];
    },
  },
  mounted() {
    window.addEventListener('keydown', this.handleShortcuts);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleShortcuts);
  },
  methods: {
    handleShortcuts(e) {
      if (!e.ctrlKey) return;
      const key = e.key.toLowerCase();
      if (key === 'j') {
        this.currentTab = 'journal';
        e.preventDefault();
      } else if (key === 't') {
        this.currentTab = 'tasks';
        e.preventDefault();
      } else if (key === 'g') {
        this.currentTab = 'goals';
        e.preventDefault();
      }
    },
  },
});

app.mount('#app');


const notifyBtn = document.getElementById('notifyBtn');
notifyBtn.addEventListener('click', async () => {
    if (!('Notification' in window)) return;
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
        new Notification('Notifications enabled!');
    }
});
