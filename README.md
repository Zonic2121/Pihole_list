# Pihole_list

The list can be used by a pihole as a block list. It contains the entries as regex.

The purpose of this project was to export the blocklist from the firefox extention (EFF Privacy Badger) and convert it into a list format for Pihole in regex format to use as "dynamic generated blocklist"

The python script converts the "privacy_badger.json" into "pihole_regex_list.txt"

Features of the script.
It tries to open pihole_regex_list.txt before creating a new one, so it will update the present file.
1) Add new entries which are not in the list yet.
2) Removes entries which are not marked as "block" in the json anymore (remove obsolete entries)
3) It is not deleting entries which are not in the json anymore, this is to be able to extend the pihole list from different json foles (from different users or PC/MAC/UNIX maschines.
