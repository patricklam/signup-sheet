signup-sheet
============

A simple Django app to sign up for timeslots.

To initialize the app, visit the hidden URL `/signup/init` while logged in as superuser. This will initialize the database and optionally populate it with dummy data. You can then populate groups using input with the following syntax:

```GroupA.txt:Group UW userids: xyz, abc, def```

(Conveniently, this is the output from the command `grep "Group UW userids:" *.txt`
in a format that I've specified to my students.)

The app's operation is self-explanatory. While logged in as superuser, it is also possible to view the UI as another user. Just check the unlabelled checkbox to actually view the setuid; no checkbox = root permissions.
