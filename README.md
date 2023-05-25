# tts-sha1-check Background
This script verifies that Tabletop Simulator (TTS) mod files which are downloaded from steamcloud are free of corruption.  Steamcloud files store the SHA-1 hash value as part of the filename.  This script computes the SHA-1 value of the file and compares it to the filename.  It can optionally move any corrupt files to a specified backup directory.  The script also creates a "sha1-verified.txt" file in each directory, so subsequent runs do not re-check previously verified files.

# Usage
usage: sha1-check.py [-h] [-b BACKUP_PATH] mod_path

*NOTE: Do not include a trailing '\\' character as part of the paths.  This causes bad things to happen when windows is passing the arguments to python.*

# Sample Run
```
> python .\sha1-check.py -b 'C:\Program Files (x86)\Steam\steamapps\common\Tabletop Simulator\Tabletop Simulator_Data\Mods\Backup' 'C:\Program Files (x86)\Steam\steamapps\common\Tabletop Simulator\Tabletop Simulator_Data\Mods'
Mod dir: C:\Program Files (x86)\Steam\steamapps\common\Tabletop Simulator\Tabletop Simulator_Data\Mods
Backup dir: C:\Program Files (x86)\Steam\steamapps\common\Tabletop Simulator\Tabletop Simulator_Data\Mods\Backup

Mods
Assetbundles...10
Audio...9
Images...271
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc1618436850079337721CDA12E1FE47ACE641FA900276D767B1B2BDF4171.png
Images...1656
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc18312883045980909260D77E2898E057E2E7FE5A6C79D4BF1645AEA13EA.png
Images...1657
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc1831288304598095336DBBFB49EB54A3F465BD96FF4F9DE8EFB8DABF9C3.png
Images...2285
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc1924753791401522680E1E74BBA475E22A294787709B4F8BCF9ACC496C2.png
Images...2489
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc2058745292939655971C0C5C09238A5B80D7707C1CB60F8780A0E8F8B12.png
Images...3017
  SHA-1 Mismatch in httpcloud3steamusercontentcomugc97226460688706947F6690C96E2D10AFA10002C73EB2634780D4CE29F.png
  Found matching raw file: httpcloud3steamusercontentcomugc97226460688706947F6690C96E2D10AFA10002C73EB2634780D4CE29F.rawt
Images...3019
Models...142
PDF...48
Text
Translations
```
