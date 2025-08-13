const THEME_KEY = 'selectedTheme';

export function getSelectedTheme(): string | null {
  return localStorage.getItem(THEME_KEY);
}

export function setSelectedTheme(theme: string): void {
  localStorage.setItem(THEME_KEY, theme);
}

export default { getSelectedTheme, setSelectedTheme };
