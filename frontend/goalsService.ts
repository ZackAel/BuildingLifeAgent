export interface Goal {
    id: number;
    title: string;
    startDate: Date;
    targetDate: Date;
    completed: boolean;
  }
  
  const STORAGE_KEY = 'goals';
  
  function reviveGoal(data: any): Goal {
    return {
      ...data,
      startDate: new Date(data.startDate),
      targetDate: new Date(data.targetDate),
    } as Goal;
  }
  
  export default {
    loadGoals(): Goal[] {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return parsed.map(reviveGoal);
    },
  
    saveGoals(goals: Goal[]) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(goals));
    },
  
    calculateProgress(goal: Goal): number {
      if (goal.completed) return 100;
      const now = new Date();
      const start = goal.startDate;
      const end = goal.targetDate;
      if (now <= start) return 0;
      if (now >= end) return 100;
      const total = end.getTime() - start.getTime();
      const progress = now.getTime() - start.getTime();
      return Math.min(100, Math.max(0, (progress / total) * 100));
    }
  };