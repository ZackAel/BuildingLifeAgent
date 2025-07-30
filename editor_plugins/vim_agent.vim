" BuildingLifeAgent Vim plugin
" Add tasks, complete tasks or log mood directly from Vim

function! AgentAddTask()
    let l:task = input('New task: ')
    if len(l:task)
        call system('python - <<EOF\nfrom tasks import load_tasks, save_tasks\ntasks = load_tasks()\ntasks.append("'.shellescape(l:task,1).'")\nsave_tasks(tasks)\nEOF')
        echo "Task added!"
    endif
endfunction
command! AgentAddTask call AgentAddTask()

function! AgentCompleteTask()
    let l:task = input('Task to complete: ')
    if len(l:task)
        call system('python - <<EOF\nfrom tasks import complete_task\ncomplete_task("'.shellescape(l:task,1).'")\nEOF')
        echo "Task completed!"
    endif
endfunction
command! AgentCompleteTask call AgentCompleteTask()

function! AgentLogMood()
    let l:mood = input('Mood: ')
    if len(l:mood)
        call system('python - <<EOF\nfrom mood import log_mood\nlog_mood("'.shellescape(l:mood,1).'")\nEOF')
        echo "Mood logged!"
    endif
endfunction
command! AgentLogMood call AgentLogMood()

