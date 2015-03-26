# smpv
A rock stupid version control system - currently not for prime time - need to fix some
really bad naming conventions revision v. version inherited from where it was last used - yeesh

First of all I will say what smpv is not
- It is NOT a fully fledged version control environment
- it is NOT a replacement for a fully fledged version control environment
- it is NOT Git, CVS, RCS, etc.

What it is
a simple, serverless, file version system for artists to use to get around folder
bloat and rediculous file names with words like "final", and "mostfinal", and 
"mostestfinalist" and "no_really_this_one_is_final".

All it does do is 
- make a a subfolder in the current location named .smpv
- copy the file into it and rename it to something in smpv w a number
- records this in a .INI "database"
- changes permissions to the original file to read only
- allows you to check ou the file
-- registering this in the database and changing file permissions
- allows you to check the file back in
-- registering with database
-- giving this a comment recorded with the revision in the database
- revert to a previous revision
- get the history for a file
- get the status of a file
- has a separate notion of version and published revision (need to switch these - bad TIP naming)
-- does nothing with that notion except tag it in the database - for another system?

usage:
smpv --file filename [--add, etc]

(currently this list is inaccurate - I will fix it)
Usage: smpv [options]

Options:
  -h, --help            show this help message and exit
  --add
  --checkin
  --checkout
  --revert
  --recall_vers=I_RECALL_VERS
  --recall_file=S_RECALL_FILE_NAME
  --revup_vers=I_REVUP_VERS
  --revup_rev=I_REVUP_REV
  --history
  --status
  --file=S_FILE_NAME
  --comment=S_COMMENT
