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
folders.  Attributes of a repository include

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

