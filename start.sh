#!/usr/bin/env bash

SESSION="pos"

# If the session already exists, attach to it
if tmux has-session -t "$SESSION" 2>/dev/null; then
    exec tmux attach -t "$SESSION"
fi

tmux new-session -d -s "$SESSION" -c "$(pwd)"

# Left pane: Neovim
tmux send-keys -t "$SESSION" "nvim ." C-m

# Right pane
tmux split-window -h -t "$SESSION" -c "$(pwd)"

# Top-right: Docker
tmux send-keys -t "$SESSION:0.1" "docker compose up" C-m

# Bottom-right
tmux split-window -v -t "$SESSION:0.1" -c "$(pwd)"

# Bottom-right: FastAPI
tmux send-keys -t "$SESSION:0.2" "uv run fastapi dev app/main.py" C-m

tmux select-layout -t "$SESSION" main-vertical

tmux attach -t "$SESSION"
