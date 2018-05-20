#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all drive file ACLs for Team Drive files shared with a list of specified domains
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment. Set DOMAIN_LIST.
# Usage:
# 1: List all Team Drives, if you don't want all users, replace all users with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv all users print teamdrives role organizer fields id,name
# 2: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 3: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv TeamDrives.csv gam user ~User print filelist select teamdriveid ~id fields teamdriveid id title permissions
# 4: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,domain,withLink"
#    that lists the driveFileIds and permissionIds for all ACLs from the specified domains.
#    (n.b., role, type, emailAddress and title are not used in the next step, they are included for documentation purposes)
#  $ python GetSharedWithDomainTeamDriveACLs.py filelistperms.csv deleteperms.csv
# 5: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 6: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]
# Specify desired value of withLink field: True, False, Any (matches True and False)
DESIRED_WITHLINK = 'Any'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'domain', 'withLink'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'domain':
      permissions_N = mg.group(1)
      domain = row['permissions.{0}.domain'.format(permissions_N)]
      withLink = row.get('permissions.{0}.withLink'.format(permissions_N), str(row.get('permissions.{0}.allowFileDiscovery'.format(permissions_N)) == 'False'))
      if domain in DOMAIN_LIST and (DESIRED_WITHLINK == 'Any' or DESIRED_WITHLINK == withLink):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'domain': domain,
                            'withLink': withLink})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
