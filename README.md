# renpy-line-brkr
A command-line program which adds newline characters to your Text Displayables in your Ren'Py files.

## Introduction
As said on [Ren'Py's Website](https://www.renpy.org/), "Ren'Py is a visual novel engine – used by thousands of creators from around the world – that helps you use words, images, and sounds to tell interactive stories that run on computers and mobile devices." 

By default, Ren'Py displays any [Say Statement](https://www.renpy.org/doc/html/dialogue.html#say-statement) dialogue at a set position on the screen. For most developers, this default position is perfectly fine, and they can easily tailor this position to their needs if needed. However, this position remains the same for all Say Statement text. This isn't inherently problematic, but for developers who desire more freedom when it comes to positioning text their options are limited. Ren'Py [Text Displayables](https://www.renpy.org/doc/html/displayables.html#text-displayables) empower developers to position text anywhere on screen, but at the cost of developer flexibility. Unlike other common forms of Ren'Py [Text](https://www.renpy.org/doc/html/text.html), Text Displayables are treated as *images* instead of character data. As a result, Text Displayables have the possibility of rendering text off-screen if they're not positioned at the center of the screen.

For example, Ren'Py will center and break text within a Text Displayable as if it were centered on screen, so the following Text Displayable (including the *pause* keyword):
```
show text "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
pause
```
Will render the Text Displayable like this:

![Text-Displayable](images/Text-Displayable-1.png)

However, if you position the Text Displayable using Ren'Py [Animation and Transformation Language](https://www.renpy.org/doc/html/atl.html) anywhere else (in this case to the leftmost center of the screen):
```
show text "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.":
    pos(0.0, 0.5)
pause
```
Will render the Text Displayable like this:

![Text-Displayable](images/Text-Displayable-2.png)

<br/>

## User Guide
asdads

<br/>

### Overview & Use

<br/>

### Required Flags

<br/>

#### Read Flag
-r/--read  

<br/>

#### Write Flags
##### Write
-w/--write

<br/>

##### Overwrite
-o/--overwrite

<br/>

### Optional Flags
Ordered by relevancy

<br/>

#### Text Length Flag
-t/--text-length

<br/>

#### Line Inclusion/Exclusion Flags
##### -x/--exclude-line & -n/--include-line

<br/>

##### Argument Format

<br/>

#### Data Length Flag
-d/--data-length

<br/>

#### Image Length Flag
-i/--image-length

<br/>


#### Space Length Flag
-s/--space-length

<br/>


## Program Behavior
