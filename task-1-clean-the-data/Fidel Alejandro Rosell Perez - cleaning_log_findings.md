# Task 1 — Cleaning findings

| Decision | Action | Records |
| --- | --- | ---: |
| Inconsistent column name formatting | Standardized column names to lowercase snake_case | 4 |
| Missing or empty ticket body | Dropped records | 1 |
| Inconsistent whitespace in ticket text | Normalized repeated whitespace, tabs, line breaks, and leading/trailing spaces | 47 |
| Unicode normalization issue in ticket text | Normalized Unicode characters to their standard form | 1 |
| Inconsistent department formatting | Trimmed whitespace and normalized casing | 29650 |
| PII found in ticket text | Filtered PII | 22 |
| HTML break tags | change | 652 |
| Broken break markers | change | 19 |
| Missing space after sentence punctuation | change | 1830 |
| Missing space after a comma | change | 1912 |
| Curly single quotes | change | 71 |
| Square-bracket template slots | change | 949 |
| Angle-bracket placeholders | replace PII | 987 |

## 1. Inconsistent column name formatting

**What the issue was.** Inconsistent column name formatting

**Why it is an issue.** Creates consistent field names and makes downstream processing easier.

**How it was addressed.** Standardized column names to lowercase snake_case

**Records affected.** 4

**Representative ticket ids.** none

**Risk.** Column names are changed only; the underlying record values are not modified.

## 2. Missing or empty ticket body

**What the issue was.** Missing or empty ticket body

**Why it is an issue.** Body is the primary text input for the ticket classification model.

**How it was addressed.** Dropped records

**Records affected.** 1

**Representative ticket ids.** 28902

**Risk.** Removing records may introduce bias if missing bodies are associated with particular departments.

## 3. Inconsistent whitespace in ticket text

**What the issue was.** Inconsistent whitespace in ticket text

**Why it is an issue.** Whitespace variations do not normally add meaning to support-ticket text and can create unnecessary textual variation.

**How it was addressed.** Normalized repeated whitespace, tabs, line breaks, and leading/trailing spaces

**Records affected.** 47

**Representative ticket ids.** 2047, 2262, 4530, 6805, 7270, 7907, 8485, 9070, 9097, 9135, 12724, 14001, 15842, 15854, 16206, 18762, 21596, 22215, 22776, 23252, 24175, 24282, 27555, 27621, 28336, 28479, 28496, 28499, 28562, 28636, 28794, 28874, 28880, 28940, 28961, 28972, 28977, 29045, 29046, 29069, 29077, 29127, 29427, 29468, 29575, 29588, 29630

**Risk.** Some unusual whitespace may have intentional formatting meaning, although this is unlikely in ordinary ticket text.

## 4. Unicode normalization issue in ticket text

**What the issue was.** Unicode normalization issue in ticket text

**Why it is an issue.** Unicode normalization ensures consistent representation of characters across systems.

**How it was addressed.** Normalized Unicode characters to their standard form

**Records affected.** 1

**Representative ticket ids.** 29291

**Risk.** Some Unicode characters may have intentional formatting meaning, although this is unlikely in ordinary ticket text.

## 5. Inconsistent department formatting

**What the issue was.** Inconsistent department formatting

**Why it is an issue.** department is a categorical field and equivalent values should use a consistent representation.

**How it was addressed.** Trimmed whitespace and normalized casing

**Records affected.** 29650

**Representative ticket ids.** 1, 2, 3, 4, 5

**Risk.** Changing casing is safe for categorical normalization, but semantically different labels must not be merged without domain evidence.

## 6. PII found in ticket text

**What the issue was.** PII found in ticket text

**Why it is an issue.** PII should not be stored in the database.

**How it was addressed.** Filtered PII

**Records affected.** 22

**Representative ticket ids.** 10995, 28268, 28301, 28521, 28548, 28603, 28641, 28709, 28784, 28800, 28803, 28954, 28971, 29085, 29139, 29174, 29237, 29366, 29433, 29458, 29630, 29644

**Risk.** PII may be sensitive and should not be stored in the database.

## 7. HTML break tags

**What the issue was.** HTML break tags

**Why it is an issue.** Break tags are template markup and do not describe the customer's request.

**How it was addressed.** change

**Records affected.** 652

**Representative ticket ids.** 630, 633, 795, 796, 914

**Risk.** The pattern is limited to br so it does not delete other tags.

## 8. Broken break markers

**What the issue was.** Broken break markers

**Why it is an issue.** These closings are a line break written without a finished br tag.

**How it was addressed.** change

**Records affected.** 19

**Representative ticket ids.** 19862, 28321, 28425, 28471, 28568

**Risk.** Only the broken <brWarm tag and the doubled brbr run are matched.

## 9. Missing space after sentence punctuation

**What the issue was.** Missing space after sentence punctuation

**Why it is an issue.** Two sentences were concatenated, so the model sees one token instead of two.

**How it was addressed.** change

**Records affected.** 1830

**Representative ticket ids.** 1, 2, 3, 4, 5

**Risk.** The next character must be a capital, so names such as Node.js stay intact.

## 10. Missing space after a comma

**What the issue was.** Missing space after a comma

**Why it is an issue.** The comma is glued to the next word in openings and signature lines.

**How it was addressed.** change

**Records affected.** 1912

**Representative ticket ids.** 1, 2, 3, 4, 5

**Risk.** The space is inserted at the first letter only, so nameacc_num stays one token.

## 11. Curly single quotes

**What the issue was.** Curly single quotes

**Why it is an issue.** A curly apostrophe and an ASCII apostrophe are the same word with two code points.

**How it was addressed.** change

**Records affected.** 71

**Representative ticket ids.** 28296, 28305, 28309, 28333, 28338

**Risk.** The curly mark is treated as an apostrophe.

## 12. Square-bracket template slots

**What the issue was.** Square-bracket template slots

**Why it is an issue.** Bracketed slots such as [Your Name] are unfilled template fields.

**How it was addressed.** change

**Records affected.** 949

**Representative ticket ids.** 32, 34, 48, 53, 81

**Risk.** A broad bracket pattern also matches a JSON fragment that names a real product.

## 13. Angle-bracket placeholders

**What the issue was.** Angle-bracket placeholders

**Why it is an issue.** Angle-bracket slots such as <tel_num> and <name> are redacted fields written as markup.

**How it was addressed.** replace PII

**Records affected.** 987

**Representative ticket ids.** 630, 633, 795, 796, 914

**Risk.** This pattern also matches break tags, so those rows are counted here as well.