---
type: ink-reference
source: WritingWithInk.md
part: 1
section: "Content"
tags: ["ink-language"]
---

<!-- search: Developers search for this when: writing basic ink text, comments, tags, marking up lines, hashtags, TODO markers -->

# Content
*Part 1 of Writing with ink*


### The simplest ink script

The most basic ink script is just text in a .ink file.

```ink
Hello, world!
```

On running, this will output the content, and then stop.

Text on separate lines produces new paragraphs. The script:

```ink
Hello, world!
Hello?
Hello, are you there?
```

produces output that looks the same.


### Comments

By default, all text in your file will appear in the output content, unless specially marked up.

The simplest mark-up is a comment. **ink** supports two kinds of comment. There's the kind used for someone reading the code, which the compiler ignores:

```ink
"What do you make of this?" she asked.

// Something unprintable...

"I couldn't possibly comment," I replied.

/*
	... or an unlimited block of text
*/
```

and there's the kind used for reminding the author what they need to do, that the compiler prints out during compilation:


```ink
TODO: Write this section properly!
```

### Tags

Text content from the game will appear 'as is' when the engine runs. However, it can sometimes be useful to mark up a line of content with extra information to tell the game what to do with that content.

**ink** provides a simple system for tagging lines of content, with hashtags.

```ink
A line of normal game-text. # colour it blue
```

These don't show up in the main text flow, but can be read off by the game and used as you see fit. See [Running Your Ink](RunningYourInk.md#marking-up-your-ink-content-with-tags) for more information.

