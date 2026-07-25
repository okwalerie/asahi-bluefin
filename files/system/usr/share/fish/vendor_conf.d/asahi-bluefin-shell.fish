if status is-interactive
    starship init fish | source
    zoxide init fish | source
    direnv hook fish | source
end
