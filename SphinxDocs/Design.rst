################
CloudSync Design
################

============
Introduction
============

This section explains about repositories and file objects.

------------
Repositories
------------

Files are synchronized between a folder on the local hard drive drive
of a system and a remote *repository*.  A repository can be any storage
facility capable of retaining files and keeping files organized in
folders.  Attributes of a repository include:

- Whether more than on version of a file can be saved
- The classes of storage available (if any)
- Cost of storage by class (if any)

Types of repositories can include an Amazon AWS S3 bucket or just a
file share available on the local network.

------------
File Objects
------------

Individual files in a repository are represented by *file
objects*.  File objects have attributes which include:

- Name of file (simple name and full pathname)
- Size of file, in bytes
- Billable size (if repository is cloud storage that bills by size)
- Date/time file of file
- Versions (if supported)

---------------------
Synchronization
---------------------

There are several types of synchronization between a folder on the local
hard drive (hereafter called *local folder*) and a repository.  Synchronization may take
place at the root of the local folder and repository or any sub-folder level within the
local folder and repository.

================ =======================================================================
Type             Meaning
================ =======================================================================
**Update**       Files and folders that exist or have been updated on the local folder
                 compared to those in the repository since the last sync
                 operation overwrite files and folders in the repository.  If supported
                 older versions are preserved in the repository.  Files and folders that
                 exist in the repository that are not in the source folder are left untouched.
**Replicate**    Same as **Update**, except that any files and folder that exist in the
                 repository that are not in the local folder are deleted, including older
                 versions of files, if supported.
**Synchronize**  Between the local folder and repository, and any file or folder that
                 is newer or that doesn't exist in the other is copied, overwriting the older
                 file.  If supported older versions are preserved in the repository.
**Restore**      The local folder is overwritten with the contents of the repository,
                 deleting any files in the local folder that don't exist in the repository.
                 This option may also include a timestamp, which if older versions exist
                 in the repository, the newest version not greater than that time is copied.
================ =======================================================================


