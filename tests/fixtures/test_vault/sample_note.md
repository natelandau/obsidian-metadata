---
date_created: 2022-12-22 # confirm dates are translated to strings
tags:
    - foo
    - bar
frontmatter1: foo
frontmatter2: ["bar", "baz", "qux"]
🌱: 🌿
# Nested lists are not supported
# invalid:
#     invalid:
#         - invalid
#         - invalid2
---

# Heading 1

inline1:: foo
inline1::bar baz
**inline2**:: [[foo]]
_inline3_:: value
🌱::🌿
key with space:: foo

> inline4:: foo

inline5::

foo bar [intext1:: foo] baz `#invalid` qux (intext2:: foo) foobar. #tag1 Foo bar #tag2 baz qux. [[link]]

The quick brown fox jumped over the lazy dog.

# tag3

---

## invalid: invalid

```python
invalid:: invalid
#invalid
```
