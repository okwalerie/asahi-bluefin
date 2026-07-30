# Terra, aarch64, and Ghostty

**Research date:** 2026-07-30 (UTC)
**Scope:** Fedora/Asahi-style `aarch64` availability, Terra/Subatomic versus Fedora COPR, and a non-mutating inspection of this host.

## Bottom line

- **Terra does serve `aarch64` packages; it is not x86_64-only.** The live Terra 43 and 44 primary metadata each list `ghostty` **and** `ghostty-nightly` RPMs for both `aarch64` and `x86_64`. On Terra 44 the stable RPM is `ghostty-1.3.1-1.fc44.aarch64`, and the metadata also includes the corresponding aarch64 devel/debug packages. [Live Terra 44 metadata](https://repos.fyralabs.com/terra44/repodata/repomd.xml) / [live Terra 43 metadata](https://repos.fyralabs.com/terra43/repodata/repomd.xml)
- This is stronger evidence than merely finding a spec: Terra's `f44` source tree contains stable and nightly Ghostty manifests, and the stable spec has no x86_64-only `ExclusiveArch`; the published metadata confirms the actual aarch64 build. [Terra Ghostty stable spec](https://raw.githubusercontent.com/terrapkg/packages/f44/anda/devs/ghostty/stable/ghostty.spec) · [nightly spec](https://raw.githubusercontent.com/terrapkg/packages/f44/anda/devs/ghostty/nightly/ghostty-nightly.spec)
- **Do not generalize that to every Terra package.** Terra has aarch64 build/repository support, but architecture availability remains package/build-dependency specific. Its own mock-config repository describes configurations for supported “version, architecture, or even distro,” rather than promising every package on every architecture. [Terra mock-configs README](https://github.com/terrapkg/mock-configs/blob/main/README.md)
- The common Ghostty COPRs inspected also currently expose Fedora 43/44/Rawhide **aarch64** chroots. Therefore, a COPR is **not preferable solely because this is Asahi/aarch64**. It may still be preferable when a specific maintainer, version, or narrower repository trust scope is desired. [scottames/ghostty API](https://copr.fedorainfracloud.org/api_3/project?ownername=scottames&projectname=ghostty) · [myriad-sun/ghostty API](https://copr.fedorainfracloud.org/api_3/project?ownername=myriad-sun&projectname=ghostty) · [cube1ber/ghostty API](https://copr.fedorainfracloud.org/api_3/project?ownername=cube1ber&projectname=ghostty)

## What the first-party Terra sources say

Terra identifies itself as a community Fedora repository. Its `packages` monorepo provides the normal Fedora installation path and a separate immutable/atomic path: install Terra's Subatomic `.repo` file, then layer `terra-release` with `rpm-ostree`. [Terra packages README — installation](https://github.com/terrapkg/packages/blob/f44/README.md#installation)

The first-party Subatomic manifest is deliberately architecture-neutral: its repository URL is `https://repos.fyralabs.com/terra$releasever`, not an x86_64 URL, and it is the file Terra tells atomic users to install. [Subatomic `terra.repo`](https://github.com/terrapkg/subatomic-repos/blob/main/terra.repo) · [Subatomic manifests README](https://github.com/terrapkg/subatomic-repos/blob/main/README.md)

The live `terra44` repository metadata contains both architectures in one RPM-MD repository. Relevant results observed on 2026-07-30:

| Release | Stable Ghostty | Nightly Ghostty |
|---|---|---|
| Terra 44 | `ghostty-1.3.1-1.fc44.aarch64.rpm` and `.x86_64.rpm` | `ghostty-nightly-1.3.2~tip^20260318gitd3bd224-1.fc44.aarch64.rpm` and `.x86_64.rpm` |
| Terra 43 | `ghostty-1.3.1-1.fc43.aarch64.rpm` and `.x86_64.rpm` | `ghostty-nightly-1.3.2~tip^20260318gitd3bd224-1.fc43.aarch64.rpm` and `.x86_64.rpm` |

The primary metadata is zstd-compressed and linked from the two `repomd.xml` documents above; it is the repository's authoritative package index.

## Ghostty provenance and COPR comparison

Ghostty upstream explicitly says that it relies on **downstream package maintainers** for end-user distribution. It publishes signed, stable source tarballs and gives packagers target-architecture build guidance (`-Dcpu=baseline` and `-Dtarget=$arch-$os-$abi`); it does **not** designate Terra or any COPR as an official upstream Fedora channel. [Ghostty `PACKAGING.md`](https://github.com/ghostty-org/ghostty/blob/main/PACKAGING.md)

Terra's Ghostty spec follows that upstream model: it fetches Ghostty's signed release tarball from `release.files.ghostty.org`, verifies it with the upstream minisign public key, and builds using the target RPM/Zig macros. [Terra stable spec](https://raw.githubusercontent.com/terrapkg/packages/f44/anda/devs/ghostty/stable/ghostty.spec) · [upstream signing/build instructions](https://github.com/ghostty-org/ghostty/blob/main/PACKAGING.md#source-tarballs)

The inspected COPR project APIs show these aarch64 chroots:

| COPR | aarch64 chroots advertised by its API |
|---|---|
| `scottames/ghostty` | Fedora 43, Fedora 44, Rawhide |
| `myriad-sun/ghostty` | Fedora 43, Fedora 44, Rawhide |
| `cube1ber/ghostty` | Fedora 43, Fedora 44, Rawhide; also EPEL 10 |

These are separate community-maintained COPR repositories, not upstream Ghostty repositories. Their project descriptions identify the packages as published to COPR and direct application bugs upstream while package bugs go to the respective packaging project; assess the selected COPR maintainer and update cadence independently. [scottames project API](https://copr.fedorainfracloud.org/api_3/project?ownername=scottames&projectname=ghostty) · [myriad-sun project API](https://copr.fedorainfracloud.org/api_3/project?ownername=myriad-sun&projectname=ghostty) · [cube1ber project API](https://copr.fedorainfracloud.org/api_3/project?ownername=cube1ber&projectname=ghostty)

### Recommendation for an immutable Bluefin/Asahi host

For **Ghostty on aarch64**, either source has current Fedora 43/44 evidence. Choose based on repository policy, not CPU architecture:

1. If Terra is already an approved repository for the image, its first-party Subatomic flow is the more coherent choice: one Terra configuration, its signed metadata, and demonstrated aarch64 stable/nightly Ghostty builds.
2. If the policy is to minimize third-party repository scope and Ghostty is the only need, a single well-reviewed Ghostty COPR can be a reasonable narrower alternative—but it is not more “official” to Ghostty and offers no demonstrated aarch64 advantage over Terra.
3. Treat both as third-party downstream packaging. Pin the exact project/repository decision in image configuration, rather than assuming a package source is endorsed by Ghostty upstream.

## Live host evidence (non-destructive)

This particular host is **x86_64**, not the target Asahi machine. Commands were run only to query state on 2026-07-30:

- `rpm-ostree status` reports an image deployment from `ghcr.io/ublue-os/ucore:stable`; its only requested layered packages are `emacs-nw` and `fail2ban`.
- `rpm -q ghostty` returned `package ghostty is not installed`; no Ghostty Flatpak app or `ghostty` executable was found in the inspected standard locations.
- `dnf repolist --all` showed no Terra or Ghostty COPR. The only COPR definitions found were `ublue-os/packages` and `ublue-os/staging`, both disabled. Their repo files use `$basearch` but do not name Ghostty.

Accordingly, there is **no installed Ghostty RPM origin and no installed Ghostty COPR approach on this host to compare or preserve**. The report intentionally makes no package/repository configuration changes.
