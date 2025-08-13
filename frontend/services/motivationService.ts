export interface JournalEntry {
    timestamp: string;
    title: string;
    text: string;
  }
  
  export interface MotivationData {
    goals: string[];
    journal: JournalEntry[];
    completed: string[];
  }
  
  export async function fetchMotivationData(): Promise<MotivationData> {
    const [goalsRes, journalRes, completedRes] = await Promise.all([
      fetch('/goals'),
      fetch('/journal?count=5'),
      fetch('/tasks/completed'),
    ]);
    const goals = await goalsRes.json();
    const journal = await journalRes.json();
    const completed = await completedRes.json();
    return { goals, journal, completed };
  }
  
  export function analyzeMotivation(data: MotivationData): string {
    const goalCount = data.goals.length;
    const completedCount = data.completed.length;
    const lastEntry = data.journal[data.journal.length - 1];
    let message = `You have ${goalCount} goals and completed ${completedCount} tasks recently.`;
    if (lastEntry) {
      message += ` Last reflection: "${lastEntry.text}".`;
    }
    return message + ' Keep up the great work!';
  }
  
  export async function getMotivationMessage(): Promise<string> {
    const data = await fetchMotivationData();
    return analyzeMotivation(data);
  }
  
  export function startMotivationRefresh(
    callback: (msg: string) => void,
    intervalMs = 3600000
  ): () => void {
    let cancelled = false;
    async function refresh() {
      if (cancelled) return;
      const msg = await getMotivationMessage();
      callback(msg);
    }
    refresh();
    const handle = setInterval(refresh, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(handle);
    };
  }
  
  