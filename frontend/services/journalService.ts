export interface JournalEntry {
  text: string;
  timestamp: number;
}

const STORAGE_KEY = 'journalEntries';

export async function saveEntry(text: string): Promise<JournalEntry> {
  const entry: JournalEntry = { text, timestamp: Date.now() };
  const entries = await getEntries();
  entries.push(entry);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  return entry;
}

export async function getEntries(): Promise<JournalEntry[]> {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed: JournalEntry[] = JSON.parse(raw);
    return parsed.sort((a, b) => b.timestamp - a.timestamp);
  } catch (e) {
    console.error('Failed to parse journal entries', e);
    return [];
  }
}
