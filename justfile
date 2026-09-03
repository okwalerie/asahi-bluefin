# Maintainer commands for the Asahi Bluefin image repository.
# Requires: GitHub CLI (`gh`) authenticated with access to okwalerie/asahi-bluefin.

set shell := ["bash", "-euo", "pipefail", "-c"]

repo := "okwalerie/asahi-bluefin"
workflow := "bluebuild"

# A bare `just` is read-only: list existing builds rather than dispatching one.
default: builds

# Dispatch an arm64 image build for a ref (default: main).
build ref="main":
    gh auth status --hostname github.com
    gh workflow run "{{ workflow }}" --repo "{{ repo }}" --ref "{{ ref }}"
    echo "Dispatched {{ workflow }} for {{ ref }}. Run 'just builds' to find the new run."

# Show recent image builds, including their GitHub URLs.
builds:
    gh run list --repo "{{ repo }}" --workflow "{{ workflow }}" --limit 10 --json databaseId,status,conclusion,headBranch,createdAt,url --jq '.[] | [.databaseId, .status, (.conclusion // "-"), .headBranch, .createdAt, .url] | @tsv'

# Watch an explicitly selected GitHub Actions run until it completes.
watch run:
    gh run watch "{{ run }}" --repo "{{ repo }}" --exit-status
