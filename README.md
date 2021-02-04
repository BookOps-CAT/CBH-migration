# CBH-migration
 Analysis and migration scripts for BHS/NYU Aleph bibliographic data


## To-do
+ Analyze item record data for mapping to Sierra
+ Create an item record crosswalk from Aleph to Sierra
+ Investivate holdings records
+ remove finding aids records from the set after all manipulation is completed (load separately or consider refreshing metadata by a fresh export from ArchivesSpace); records can be identified by originally found 099 tag or Z30$B value "Archives - Manuscripts"
+ analyze subject headings thesauri used by CBH and add to approved vocabularies in Sierra
+ create 099 based on item record (Z30) data

## Done
+ files preped in MarcEdit to enforce UTF-8 chr encoding



## References
+ [MARC21 Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
+ [Mapping BHS/NYU Aleph bibliographic and item records](https://docs.google.com/spreadsheets/d/19CPV3APa_wotCb2KLEjoiJF8IKdmbhuHEnqvFdqDhmQ/edit?usp=sharing)


## Notes
+ control numbers - NYU/Aleph control number is an internal number while BPL uses OCLC number -> replace BHS 001 with OCLC # taken from 035$a (add prefix)
+ item record encoded in field Z30
+ some BHS records include 099 field (these records include archival collection id in 099)
+ holdings dump duplicates Z30 item record data - no need to worry about it (verify in all records file)
+ ask BC staff how their holdings/special notes in 5xx are recorded
+ can Z30-item tag subfields repeat?
+ number of subfields in item rec:
    + 12: 16843,
    + 13: 14085,
    + 11: 4878,
    + 15: 2188,
    + 14: 1722,
    + 16: 88,
    + 17: 68,
    + 18: 46,
    + 19: 32,
    + 21: 10, - largest has 21 subfields
    + 10: 5,  - smallest 5 subfields
    + 20: 5
    what subfields reapeat?: $m

    only 1 record has more than 2 $m: 001  000405547 (looks like error) - removed dup

+ Training Sierra bib import tests:
    + very long notes: b123708217
    + caret in 007 tag: b112313929 (training server old load table overlaid existing bib based on 001 match)
    + import of 590: b123708229 (accepted but highlighted as a mistake in red in bib display in Sierra)
    + import of 699 tag: b123708230 (accepted but hightlighted as an error in bib display)
    + import of 796 tag: b123708242 - tag rejected by load table (no mapping) - missing (move data to 700 to mitigate)

+ Records without call number: ['ocm12180664', 'ocm36531175', 'ocm24344329', 'ocm58769563', 'ocm36813841', 'on1027967459', 'ocm46243282', 'ocn480560395', 'ocm46547939', 'ocm30581624', 'ocm07164683', 'ocm08133824', 'cbh-000729']