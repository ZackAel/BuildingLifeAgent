#!/bin/bash
# BuildingLifeAgent shell prompt integration
# Source this file in your shell:
#   source /path/to/agent_prompt.sh

agent_prompt() {
    local mood_ascii
    mood_ascii=$(python - <<'PY'
from mood import get_today_mood, ascii_mood
m, _ = get_today_mood()
print(ascii_mood(m))
PY
)
    local streak
    streak=$(python - <<'PY'
from streak import get_current_streak
print(get_current_streak())
PY
)
    local task
    task=$(python - <<'PY'
from tasks import load_tasks
tasks = load_tasks()
print(tasks[0] if tasks else 'no tasks')
PY
)
    PS1="[\u@\h \W] $mood_ascii🔥$streak ➜ $task \$ "
}
PROMPT_COMMAND=agent_prompt
# ring terminal bell when sourced
printf '\a'
