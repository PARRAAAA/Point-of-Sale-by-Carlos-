#!/usr/bin/env bash

SESSION="pos"
DIR="$(pwd)"

# If session already exists, attach/switch to it
if tmux has-session -t "$SESSION" 2>/dev/null; then
    if [ -n "$TMUX" ]; then
        exec tmux switch-client -t "$SESSION"
    else
        exec tmux attach -t "$SESSION"
    fi
fi

# Create new tmux session
tmux new-session -d -s "$SESSION" -c "$DIR"

# Left pane: Docker compose detached + live logs
tmux send-keys -t "$SESSION:0.0" "docker compose up -d && docker compose logs -f" C-m

# Right pane: free terminal in project folder
tmux split-window -h -t "$SESSION:0.0" -c "$DIR"

# Make both panes 50/50
tmux select-layout -t "$SESSION" even-horizontal

# Focus right pane
tmux select-pane -t "$SESSION:0.1"

# Attach/switch
if [ -n "$TMUX" ]; then
    exec tmux switch-client -t "$SESSION"
else
    exec tmux attach -t "$SESSION"
fi
