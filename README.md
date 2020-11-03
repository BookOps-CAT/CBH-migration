# CBH-migration
 Analysis and migration scripts for BHS/NYU Aleph bibliographic data


## To-do
+ Analyze item record data for mapping to Sierra
+ Create an item record crosswalk from Aleph to Sierra
+ Investivate holdings records

## Done
+ files preped in MarcEdit to enforce UTF-8 chr encoding



## References
+ [MARC21 Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
+ [Mapping BHS/NYU Aleph bibliographic and item records](https://docs.google.com/spreadsheets/d/19CPV3APa_wotCb2KLEjoiJF8IKdmbhuHEnqvFdqDhmQ/edit?usp=sharing)


## Notes
+ control numbers - NYU/Aleph control number is an internal number while BPL uses OCLC number -> replace BHS 001 with OCLC # taken from 035$a (add prefix)
+ item record encoded in field Z30
+ some BHS records include 099 field (remove!)
+ holdings dump duplicates Z30 item record data - no need to worry about it (verify in all records file)
+ ask BC staff how their holdings/special notes in 5xx are recorded
+ can Z30-item tag subfields repeat?
+ # of subfields in item rec:
    12: 16843,
    13: 14085,
    11: 4878,
    15: 2188,
    14: 1722,
    16: 88,
    17: 68,
    18: 46,
    19: 32,
    21: 10, - largest has 21 subfields
    10: 5,  - smallest 5 subfields
    20: 5
    what subfields reapeat?: $m

    only 1 record has more than 2 $m: 001  000405547 (looks like error)