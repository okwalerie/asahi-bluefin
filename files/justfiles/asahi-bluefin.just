# concise operational entry points for this image; available through blujust.

# show the booted deployment and update/m1n1 units
status:
    bootc status
    systemctl --no-pager --full status uupd.timer asahi-bluefin-update-m1n1.service || true

# stage os updates and update flatpaks and brew without forcing a reboot
update:
    sudo systemctl start uupd.service
    systemctl --no-pager --full status uupd.service || true

# grant the current user access to claude cowork's kvm virtualization path
enable-cowork:
    sudo usermod -aG kvm "$USER"
    @echo "log out and back in before starting cowork"

# install or refresh fast-moving ai developer tools in mutable homebrew state
install-ai-cli:
    #!/usr/bin/env bash
    set -euo pipefail

    brew=/home/linuxbrew/.linuxbrew/bin/brew
    if ((EUID == 0)); then
      echo "run this as the desktop user, not root" >&2
      exit 1
    fi
    if [[ ! -x $brew ]]; then
      echo "homebrew is not ready; reboot or start brew-setup.service" >&2
      exit 1
    fi

    ensure_formula() {
      if "$brew" list --formula "$1" >/dev/null 2>&1; then
        "$brew" upgrade "$1"
      else
        "$brew" install "$1"
      fi
    }
    ensure_cask() {
      if "$brew" list --cask "$1" >/dev/null 2>&1; then
        "$brew" upgrade --cask --greedy "$1"
      else
        "$brew" install --cask "$1"
      fi
    }

    ensure_formula hermes-agent
    ensure_formula uv
    ensure_cask codex
    ensure_cask claude-code

    "$brew" list --versions hermes-agent uv
    "$brew" list --cask --versions codex claude-code

# report the image-owned packages and system flatpaks
verify:
    rpm -q tailscale uupd chromium chezmoi emacs-pgtk ghostty starship claude-desktop-extra codex-desktop handy
    flatpak remotes --system --show-details
    flatpak --system list --app
