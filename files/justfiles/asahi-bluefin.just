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

# report the image-owned packages and system flatpaks
verify:
    rpm -q tailscale uupd chromium chezmoi emacs-pgtk ghostty starship claude-desktop-bin codex-desktop handy
    codex --version
    flatpak remotes --system --show-details
    flatpak --system list --app
