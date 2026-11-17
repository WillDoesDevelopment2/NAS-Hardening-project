# Phase 3 Plan, Part 2: Phone Backups

> **Status:** Draft v0.05 · Last updated: 17th November 2026
> **Author:** William Drummond
> **Related:** [phase3-plan.md](phase3-plan.md) (part 1, the laptop, question 2.1.4) · [01-scope-and-assets.md](01-scope-and-assets.md) (objective O-4) · [02-threat-analysis.md](02-threat-analysis.md) (T-05, T-08, T-09, T-10, T-20) · [04-design-decisions.md](04-design-decisions.md) (D-06, D-14, D-15, D-16, D-22 to D-26)
> **Note:** Drafted with AI assistance on 15th November 2026, as proposals for the owner. The owner accepted every suggestion on 15th November 2026, with the answers recorded in section 2. No change to the NAS or the phone for this part until section 5 is complete. Placeholders such as `<PHONE-USER>`, `<PHONE-TS-IP>` and `<SSD-MOUNT>` stay as placeholders in this file.

---

## 1. Goal

Back up the phone to the NAS automatically, over Tailscale (the NAS is reachable only over Tailscale, D-16 change of 15th November 2026), in a way the phone cannot use to delete what is already backed up. Photos and files go to separate folders. The set-up is a pattern that can be repeated for future devices, one account and one folder each. Nothing goes to Google or another cloud service.

What the owner asked for (15th November 2026): photos in a separate folder, files, apps and app data, and device settings that would help set up a future device. Google's backup is not acceptable to the owner. Photos and files are copied with Termux.

**What Android allows.** The phone runs Android 16, is most likely not rooted (check in 2.5), and GrapheneOS and LineageOS do not support it. Without root, Android keeps each app's data readable only by that app, so no app, including Termux, can copy another app's data. `adb backup` skips the data of almost all apps made for Android 12 or later, and Shizuku has the same rights as `adb`, so neither helps. That leaves:

| Data | How, without Google | Where it goes |
|---|---|---|
| Photos and videos | Termux, `rsync` over SSH | `photos` folder on the NAS |
| Files (documents, downloads) | Termux, `rsync` over SSH | `files` folder on the NAS |
| App data, app by app | Each app's own export, written into a `Backups` folder that is copied with the files | `files/Backups` on the NAS |
| The apps themselves (install files) | A script on the laptop pulls them over USB with `adb` | The laptop backup, encrypted on the NAS |
| Device settings | The same script saves the phone's settings values with `adb shell settings list` | The laptop backup |
| App data of apps with no export | **Not possible** on this phone without root | Accepted gap, see 2.1.4 |

## 2. Questions for the owner

Each has a suggestion to start from.

### 2.1 What is backed up

1. **Photos and videos:** `DCIM/Camera` and `Pictures/Screenshots` to `photos`. Which other picture folders do you use, for example messaging apps' saved images?
   - **Owner answer, 15th November 2026:** accepted. Other picture folders are included as they are found on the phone (any `Pictures` subfolder)
2. **Files:** `Documents`, `Download` and a new `Backups` folder to `files`. Which other folders do you use?
   - **Owner answer, 15th November 2026:** accepted, and extra folders backed up: all other folders in shared storage go to `files`, apart from the photo folders, `Android` (not readable) and thumbnail and cache folders. WhatsApp's folder under `Android/media` is added (2.1.3)
3. **Apps with their own export:** suggestion: list the apps that matter and set each one to write its backup or export into `Backups`, on its own schedule where the app has one. Common examples: Signal (encrypted backup file), an authenticator (encrypted export), contacts (`.vcf` export from the Contacts app), calendar, notes, SMS (an F-Droid SMS backup app such as "SMS Import / Export" writes a file). Which apps do you use?
   - **Owner answer, 15th November 2026:** WhatsApp is the app that matters. WhatsApp writes a local backup every night to `Android/media/com.whatsapp/WhatsApp/Databases`, and received media to `.../WhatsApp/Media`. Termux can read `Android/media` once it has all-files access, so both go to `files`. Suggestion, accepted with the rest: turn on WhatsApp's end-to-end encrypted backup with a 64-digit key kept in the password manager, so the local backup file can be restored on a new phone without Google. Whether WhatsApp writes the local file without a Google account is checked on the phone
4. **Apps with no export:** their data is not backed up. Suggestion: accept this gap in D-29, with Google's backup turned off. Review trigger: moving to a phone that GrapheneOS or LineageOS supports, where Seedvault covers apps, app data and settings without root (2.6).
   - **Owner answer, 15th November 2026:** accepted
5. **Apps and settings from the laptop:** suggestion: a script on the laptop, run by hand about once a month with the phone plugged in and USB debugging on for a few minutes. It saves:
   - the list of installed apps (`pm list packages -3` with versions)
   - each installed app's install files (`pm path`, then `adb pull`), so exact versions can be put back
   - the settings values (`settings list system`, `secure` and `global`). These include no Wi-Fi passwords
   It writes to a folder in the laptop's home folder, so the laptop's encrypted Borg backup carries it to the NAS. USB debugging is turned off again afterwards.
   - **Owner answer, 15th November 2026:** a list of installed apps, to reinstall from, is enough. App install files are not saved. Suggestion: Termux tries `pm list packages -3` in the daily job first, so no laptop is needed; if Android blocks it, the laptop script saves the list over USB. Settings values are saved by the laptop script now and then (accepted with the rest)

### 2.2 Tool and transport: Termux

1. **Termux from F-Droid** (not Google Play, whose version is out of date), with the **Termux:API** add-on for scheduling. Packages: `openssh` and `rsync`. `termux-setup-storage` gives Termux access to shared storage (photos, documents, downloads), and nothing else.
   - **Owner answer, 15th November 2026:** accepted
2. **Transport:** `rsync` over SSH, through the Tailscale app on the phone, to the SSH server that already runs on the NAS. No new service or port. Termux uses its own DNS, so the NAS is named by its Tailscale address in Termux's SSH settings.
   - **Owner answer, 15th November 2026:** accepted
3. **Account:** a dedicated `<PHONE-USER>` per device, made in OMV like `<BACKUP-USER>`: no password, SSH key login only, no sudo, in `_ssh`. The phone's SSH key is made in Termux with no passphrase, as the job runs unattended. It stays in Termux's own storage, which other apps cannot read.
   - **Owner answer, 15th November 2026:** accepted
4. **Key limits:** the NAS's `rrsync` script (part of Debian's `rsync` package) limits the key to `rsync` in one folder. Two keys, one per folder, so photos can never be overwritten while documents can be updated:
   ```
   restrict,from="<PHONE-TS-IP>",command="rrsync -wo -no-del -no-overwrite <DEVICE-PATH>/photos" ssh-ed25519 <PUBLIC-KEY-1> phone-photos
   restrict,from="<PHONE-TS-IP>",command="rrsync -wo -no-del <DEVICE-PATH>/files" ssh-ed25519 <PUBLIC-KEY-2> phone-files
   ```
   `-wo` means write only, so a stolen phone cannot read the backups back. `-no-del` refuses deletes. `-no-overwrite` keeps existing photos as they are. The options are checked against the NAS's version with `rrsync -h` before the lines are written, and `rsync` is checked as installed with `apt-cache policy rsync`. Restores are done from the NAS side (2.4.5).
   - **Owner answer, 15th November 2026:** accepted
5. **Folder layout, for future devices:** `<SSD-MOUNT>/devices/<DEVICE>/photos` and `<SSD-MOUNT>/devices/<DEVICE>/files`, each device with its own account. Owned by that account, mode 700, not shared over SMB.
   - **Owner answer, 15th November 2026:** accepted
6. **Alternatives considered:** FolderSync (Google Play) and Round Sync (F-Droid) over SFTP. Not chosen, as the owner prefers Termux. Syncthing is not suggested: it adds a new service and two ports on the NAS.
   - **Owner answer, 15th November 2026:** accepted

### 2.3 Encryption

1. **At rest:** the SSD is already encrypted (D-06), so the copies are protected if the SSD is taken out while locked. While the NAS runs, the admin account can read them.
   - **Owner answer, 15th November 2026:** accepted
2. **On the phone:** suggestion: no extra encryption for photos and files, so they stay viewable and are easy to restore. Exports that hold secrets (Signal, authenticator) are encrypted by the apps themselves, with their passwords kept in the password manager. The app install files and settings travel inside the laptop's encrypted Borg backup.
   - **Owner answer, 15th November 2026:** accepted

### 2.4 Schedule, deleted files and restores

1. **When:** suggestion: daily, using `termux-job-scheduler` with `--network unmetered --charging true`, so it runs only on Wi-Fi and while charging. Termux is exempted from battery optimisation so Android does not stop the job. The script exits without sending if the NAS cannot be reached over Tailscale.
   - **Owner answer, 15th November 2026:** accepted
2. **Deleted on the phone:** kept on the NAS, as the keys cannot delete (2.2.4). Old files are cleared by hand on the NAS.
   - **Owner answer, 15th November 2026:** accepted
3. **Overwritten documents:** the `files` key can overwrite a file with the same name, for example after ransomware on the phone. Suggestion: daily read-only Btrfs snapshots of `<SSD-MOUNT>/devices` on the NAS (the SSD is Btrfs, D-15), kept 14 days. This is a new timer on the NAS.
   - **Owner answer, 15th November 2026:** accepted
4. **Missed backups:** suggestion: the laptop's missed-backup check (D-26, phase3-changes.md section 8) also checks the newest file in each device's folders, and warns after 7 days without a new file, as a phone can go days without new photos.
   - **Owner answer, 15th November 2026:** accepted
5. **Restores:** as the keys are write only, a restore is copied from the NAS by the admin account to the laptop, then to the phone over USB, or over SMB from a share the owner sets up for the purpose.
   - **Owner answer, 15th November 2026:** accepted

### 2.5 Root on this phone

1. **How to check:** Settings, About phone, tap "Build number" seven times to turn on Developer options. In Settings, System, Developer options, look at "OEM unlocking". If the bootloader has never been unlocked, the phone is not rooted. A second check, in Termux: `su` answers `No su program found` on a phone without root.
   - **Owner answer, 15th November 2026:** accepted
2. **Rooting:** it needs the bootloader unlocked (some makers give unlock codes for some models; it wipes the phone and may void the warranty), then Magisk. It would let Neo Backup (F-Droid) copy all apps' data to the NAS. Trade-offs: an unlocked bootloader and root weaken the phone's protection if it is lost or stolen, and banking and payment apps often refuse to run. Suggestion: do not root, and accept the gap in 2.1.4.
   - **Owner answer, 15th November 2026:** accepted: no root. Root check (2.5.1) still to do

### 2.6 Future phone

1. When you move to a phone that GrapheneOS or LineageOS supports, add Seedvault for apps, app data and settings, written to a `system` folder in the same device layout. Seedvault encrypts its own backups. This closes the gap in 2.1.4.
   - **Owner answer, 15th November 2026:** accepted

## 3. Decisions to record (document 04)

Proposed numbers follow the last decision, D-28.

| Proposed | Decision | Questions |
|---|---|---|
| D-29 | What the phone backs up, no cloud backup, and app data without an export left out (accepted gap) | 2.1, 2.5, 2.6 |
| D-30 | Termux and `rsync` over Tailscale, account, `rrsync` key limits and folder layout per device | 2.2 |
| D-31 | Phone encryption, schedule, deleted files, snapshots and restores | 2.3, 2.4 |

## 4. Requirements to propose (document 03)

| Proposed | Requirement | Priority |
|---|---|---|
| SR-31 | Phone photos and files are copied to the NAS at least daily when the phone is on Wi-Fi and charging | Must |
| SR-32 | A device's backup key can only write to its own folder: no delete, no reading back, no shell, no forwarding, no other folder | Must |
| SR-33 | Files overwritten from a device can be recovered for 14 days | Should |
| SR-34 | Apps that matter write their own export into the synced `Backups` folder, and the app list, install files and settings are saved monthly through the laptop | Should |

## 5. Before any change for this part

- [x] Section 2 answered and decisions D-29 to D-31 accepted (15th November 2026)
- [x] SR-31 to SR-34 accepted, and the tests in section 6 added to document 05, section 4.5 (15th November 2026)
- [ ] Root check done (2.5.1) and the answer recorded
- [ ] Tailscale on the phone connected and approved (D-14)
- [ ] Google's backup turned off on the phone (Settings, Google, Backup), owner's choice

## 6. Draft test plan

| Proposed | Checks | Expected result |
|---|---|---|
| V-45 | Phone keys' limits: a shell, a command, SFTP, a port forward, `rsync` to another folder, reading back from the NAS, deleting with `rsync --delete`, and overwriting a photo | All refused. Overwriting a document with the `files` key works, as designed |
| V-46 | Photos and files arrive: take a photo and save a file, then wait for the next run on Wi-Fi and charging | Both appear in the right folder on the NAS. Nothing is sent on mobile data or while not charging |
| V-47 | Deleted on the phone | A photo deleted on the phone is still on the NAS after the next run |
| V-48 | Overwrite recovery | A document overwritten from the phone is recovered from the previous day's snapshot |
| V-49 | Restore to a phone | A photo and a file copied back to the phone (2.4.5) open correctly |
| V-50 | App exports and the laptop script | Each listed app's export is in `files/Backups` on the NAS. The app list, install files and settings are in the newest laptop archive |
| V-01, V-04, V-09, V-12 | Repeat | No new port or listener. One more account in `_ssh`, without sudo. SSH settings unchanged |

## 7. Draft completion criterion

Part 2 is complete when D-29 to D-31 are recorded; SR-31 and SR-32 are verified by V-45 to V-47; SR-33 and SR-34 are verified by V-48 and V-50 or deferred with a reason; V-49 passes; the app-data gap is recorded in D-29 with its review trigger; and the repeated tests match their expected results.

## 8. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.01 | 15th November 2026 | First draft: what Android allows on this phone, questions with suggestions, decisions, requirements, tests and completion criterion (drafted with AI assistance) | Owner request: photos and files, apps, app data and settings |
| 0.02 | 15th November 2026 | Google's backup removed (not acceptable to the owner). Termux with `rsync` and `rrsync` key limits replaces the sync app. App data by each app's export, apps and settings saved through the laptop with `adb`, root check and trade-offs added, phone model recorded (drafted with AI assistance) | Owner decisions |
| 0.03 | 15th November 2026 | Owner answers recorded: all suggestions accepted, all shared-storage folders backed up, WhatsApp's local backup and media included, an app list instead of install files, no root | Owner answers |
| 0.04 | 15th November 2026 | Section 5: decisions, requirements and tests recorded in documents 03, 04 and 05 | Step 1 done |
| 0.05 | 17th November 2026 | Phone make and model removed before publishing, Android version kept | Owner decision |
