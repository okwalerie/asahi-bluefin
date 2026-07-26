#!/usr/bin/env bash
# codex desktop is only a frontend: it exits before electron if the cli is absent.
# install openai's native arm64 release bundle without adding node/npm to the os.
set -euo pipefail

version=0.145.0
archive=codex-aarch64-unknown-linux-musl-bundle.tar.zst
archive_sha256=84e6cc6e218e08140982e2d28c4341a9d8c8d645dd06036ded629c6d7dc8a8fc
url="https://github.com/openai/codex/releases/download/rust-v${version}/${archive}"
destination=/usr/libexec/codex-cli

if [[ $(uname -m) != aarch64 ]]; then
  echo "error: the pinned Codex CLI bundle is for aarch64" >&2
  exit 1
fi

temporary_directory=$(mktemp -d)
trap 'rm -rf "$temporary_directory"' exit

curl --fail --location --silent --show-error \
  --output "$temporary_directory/$archive" "$url"
printf '%s  %s\n' "$archive_sha256" "$temporary_directory/$archive" |
  sha256sum --check --status

install -d -m 0755 "$destination"
tar --zstd --extract --file "$temporary_directory/$archive" \
  --directory "$destination"
chmod 0755 \
  "$destination/codex" \
  "$destination/codex-code-mode-host" \
  "$destination/codex-resources/bwrap"
ln -sfn ../libexec/codex-cli/codex /usr/bin/codex

[[ $(codex --version) == "codex-cli $version" ]]
