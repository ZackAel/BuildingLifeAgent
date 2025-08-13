export interface Task {
    id: number;
    text: string;
    done: boolean;
  }
  
  const STORAGE_KEY = 'tasks';
  
  export function getTasks(): Task[] {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return [];
    try {
      return JSON.parse(data) as Task[];
    } catch {
      return [];
    }
  }
  
  function saveTasks(tasks: Task[]): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }
  
  export function addTask(text: string): Task {
    const tasks = getTasks();
    const newTask: Task = { id: Date.now(), text, done: false };
    tasks.push(newTask);
    saveTasks(tasks);
    return newTask;
  }
  
  export function updateTask(updated: Task): void {
    const tasks = getTasks().map(t => (t.id === updated.id ? updated : t));
    saveTasks(tasks);
  }
  
  export function deleteTask(id: number): void {
    const tasks = getTasks().filter(t => t.id !== id);
    saveTasks(tasks);
  }
  
  export default { getTasks, addTask, updateTask, deleteTask };