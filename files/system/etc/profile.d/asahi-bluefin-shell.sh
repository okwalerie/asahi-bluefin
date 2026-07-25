# shellcheck shell=sh
# shell conveniences shared by interactive bash and zsh sessions.
case $- in
  *i*) ;;
  *) return ;;
esac

if [ -n "${BASH_VERSION:-}" ]; then
  eval "$(starship init bash)"
  eval "$(zoxide init bash)"
  eval "$(direnv hook bash)"
elif [ -n "${ZSH_VERSION:-}" ]; then
  eval "$(starship init zsh)"
  eval "$(zoxide init zsh)"
  eval "$(direnv hook zsh)"
fi
